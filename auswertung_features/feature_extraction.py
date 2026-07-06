from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import json
from collections import defaultdict

from models import MODELS_SUPERVISED
from features import FEATURES_TIME, FEATURES_FREQ
from parameterraum import TEST_MODELS, PARAM_GRID, ModelConfig, DataConfig, FEATURE_SET_LIBRARY

from sklearn.model_selection import LeavePGroupsOut, GroupKFold
from sklearn.base import clone
from sklearn.metrics import (confusion_matrix, ConfusionMatrixDisplay,
                             f1_score, accuracy_score, balanced_accuracy_score,
                             matthews_corrcoef, cohen_kappa_score
                             )

from scipy.fft import rfft

LABEL_COL = "Aktueller Finger"
TIME_COL = "timestamp_ms"
SENSORS = ["sensor_0", "sensor_1", "sensor_2", "sensor_3"]

DATA_CFGS = []

# Sensor 2 ist Gegenseite (Extensor-Seite)
EXT_IDX = 2
FLEX_IDXS = [0, 1, 3]

@dataclass
class TrialRow:
    subject_id: str
    hand: str
    trial_id: int
    label: int
    X: np.ndarray  # (N,4) float32

def load_session(csv_path: Path) -> pd.DataFrame | None:
    #print(f"Loading session from {csv_path}")
    df = pd.read_csv(csv_path)
    # check if df is empty
    if df.empty:
        print(f"[WARN] {csv_path}: is empty")
        return None
    # minimal sanity checks
    missing = [c for c in [LABEL_COL, TIME_COL] + SENSORS if c not in df.columns] # check if all the csv are full
    if missing:
        raise ValueError(f"Missing columns in {csv_path}: {missing}")
    df = df.sort_values(TIME_COL).reset_index(drop=True)
    return df

def split_into_label_blocks(df: pd.DataFrame, trim: int = 50, min_len: int = 300) -> list[tuple[np.ndarray, int]]:
    """Segmentiert eine Session in Label-Blöcke. Jeder Block wird zu einem Trial-Kandidaten."""
    finger = df[LABEL_COL].to_numpy()
    change = np.r_[True, finger[1:] != finger[:-1]] #Translates slice objects to concatenation along the first axis, https://numpy.org/doc/stable/reference/generated/numpy.r_.html
    # change is an array which indicates where the finger was changed
    seg_id = np.cumsum(change) - 1 #cumulative sum of change and -1 to let our segmentation start with 0

    trials = [] # extrahieren einer Bewegung
    for sid in np.unique(seg_id): # pro unique seg_id auslesen
        block = df.loc[seg_id == sid, [LABEL_COL] + SENSORS] # aus dataframe den Block extrahieren
        y = int(block[LABEL_COL].iloc[0]) # Klassenlabel auslesen
        X = block[SENSORS].to_numpy(dtype=np.float32) # get sensor data

        # abschneiden der Werte anhand des trim
        if X.shape[0] <= 2 * trim: # verwerfen von Messwerten die nciht trimbar sind
            continue
        if trim > 0:
            X = X[trim:-trim] # trim wird vorne und hinten weggeworfen

        if X.shape[0] < min_len: # wenn min_len 300 ist dann werden alle Messungen unter 600ms verworfen
            continue

        trials.append((X, y))  #zurück in die Liste packen

    return trials

def window_features_named(X: np.ndarray, cfg: DataConfig, eps: float = 1e-8):
    N, n_sensors = X.shape
    out = []
    time_names = list(cfg.time_feature_names)
    freq_names = list(cfg.freq_feature_names)

    for start in range(0, N - cfg.win + 1, cfg.step):
        w = X[start:start + cfg.win]
        feats = {}

        for name in time_names:
            v = np.asarray(FEATURES_TIME[name](w, eps=eps)).reshape(-1)
            for si, val in enumerate(v):
                feats[f"t_{name}_s{si}"] = float(val)

        if freq_names:
            ft = rfft(w, axis=0)
            s = (np.abs(ft) ** 2) / w.shape[0]
            for name in freq_names:
                v = np.asarray(FEATURES_FREQ[name](s, eps=eps)).reshape(-1)
                for si, val in enumerate(v):
                    feats[f"f_{name}_s{si}"] = float(val)

        out.append(feats)

    return out

def build_feature_table(meta: pd.DataFrame, data_cfg: DataConfig) -> pd.DataFrame:
    """
    :param meta: meta.csv mit der Übersicht der Messungen und Probanden
    :param data_cfg: Alle Daten, die ausprobiert werden sollen
    :return: dataframe mit den extractions features
    """
    rows = []
    for i, r in meta.iterrows(): # über die Tabelle iterieren
        csv_path = r["rel_path"]
        df = load_session(csv_path) # csv laden + check ob die wichtigen spalten existieren

        #Error Handling für leere dfs
        if df is None:
            continue

        blocks = split_into_label_blocks(df, trim=data_cfg.trim, min_len=data_cfg.min_len)

        # Check: idealerweise genau 5 Blöcke (0..4)
        # Wenn nicht, loggen (nicht zwingend skippen).
        labels_found = [y for (_, y) in blocks]
        if len(blocks) != 5 or sorted(set(labels_found)) != [0,1,2,3,4]:
            print(f"[WARN] {csv_path}: found blocks={len(blocks)}, labels={labels_found}")

        for trial_id, (X, y) in enumerate(blocks):
            win_dicts = window_features_named(X, cfg= data_cfg)
            # Falls nach Fensterung nix übrig bleibt -> skip
            if len(win_dicts) == 0:
                continue

            for widx, feat_dict in enumerate(win_dicts): # neubau des Dataframe mit features
                rows.append({
                    "subject_id": str(r["subject_id"]),
                    "hand": str(r["hand"]),
                    "session": str(csv_path),
                    "trial_id": trial_id,
                    "label": y, # Klassenlabel
                    "widx": widx,
                    **feat_dict
                })

    return pd.DataFrame(rows)

def trial_level_vote(df_pred: pd.DataFrame) -> pd.DataFrame:
    """
    df_pred enthält: subject_id, session, trial_id, label (true), pred (window)
    Gibt trial-level Pred via Majority Vote zurück.
    """
    gcols = ["subject_id", "session", "trial_id"]
    out = []
    for k, g in df_pred.groupby(gcols, sort=False):
        true_label = int(g["label"].iloc[0])
        # Majority vote
        pred_label = int(g["pred"].value_counts().idxmax())
        out.append({
            "subject_id": k[0],
            "session": k[1],
            "trial_id": k[2],
            "true": true_label,
            "pred": pred_label
        })
    return pd.DataFrame(out)

def plot_cm(cm: np.ndarray, classes, out_path: str, title: str):
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=classes)
    disp.plot()
    disp.ax_.set_title(title)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    disp.figure_.savefig(out_path, format="svg")
    plt.close(disp.figure_)

def eval_holdout(feature_df: pd.DataFrame,
                 train_subjects: set[str],
                 test_subjects: set[str],
                 hand: str,
                 model_name: str,
                 return_trials: bool = False) -> float | tuple[float, pd.DataFrame]:
    df = feature_df[feature_df["hand"] == hand].copy()
    df_tr = df[df["subject_id"].isin(train_subjects)]
    df_te = df[df["subject_id"].isin(test_subjects)]

    if df_tr.empty or df_te.empty:
        if return_trials:
            return float("nan"), pd.DataFrame(columns=["subject_id", "session", "trial_id", "true", "pred"])
        return float("nan")

    feat_cols = [c for c in df.columns if c.startswith("t_") or c.startswith("f_")]

    X_tr = df_tr[feat_cols].to_numpy(np.float32)
    y_tr = df_tr["label"].to_numpy(int)
    X_te = df_te[feat_cols].to_numpy(np.float32)

    model = clone(MODELS_SUPERVISED[model_name]())
    model.fit(X_tr, y_tr)
    y_pred_win = model.predict(X_te)

    df_pred = df_te[["subject_id", "session", "trial_id", "label"]].copy()
    df_pred["pred"] = y_pred_win

    trial_df = trial_level_vote(df_pred)    # columns: subject_id, session, trial_id, true, pred
    score = float(f1_score(trial_df["true"], trial_df["pred"], average="macro", zero_division=0))
    if return_trials:
        return score, trial_df
    return score

def inner_cv_score(feature_df: pd.DataFrame,
                   subjects_train_outer: list[str],
                   hand: str,
                   model_name: str,
                   n_splits: int = 4) -> float:
    subjects = np.array(subjects_train_outer)
    cv = GroupKFold(n_splits=n_splits)

    scores = []
    for tr_idx, va_idx in cv.split(subjects, groups=subjects):
        tr_sub = set(subjects[tr_idx])
        va_sub = set(subjects[va_idx])

        s = eval_holdout(feature_df, tr_sub, va_sub, hand=hand, model_name=model_name)
        scores.append(s)

    return float(np.nanmean(scores))


def nested_cv(meta: pd.DataFrame,
              hands=("l","r"),
              outer_splits=5,
              inner_splits=4,
              classes = (0, 1, 2, 3, 4),
              plot_per_outer_fold: bool = False):

    subjects_all = np.array(sorted(meta["subject_id"].astype(str).unique()))
    outer_cv = GroupKFold(n_splits=outer_splits)

    results = []

    # Cache: pro data_cfg die Feature-Tabelle einmal bauen
    feature_cache: dict[DataConfig, pd.DataFrame] = {}
    # Aggregierte CMs pro Hand über alle Outer-Folds
    cm_total = {hand: np.zeros((len(classes), len(classes)), dtype=int) for hand in hands}

    for outer_fold, (tr_idx, te_idx) in enumerate(outer_cv.split(subjects_all, groups=subjects_all)):
        outer_train_sub = subjects_all[tr_idx].tolist()
        outer_test_sub  = subjects_all[te_idx].tolist()

        outer_train_set = set(outer_train_sub)
        outer_test_set  = set(outer_test_sub)

        for hand in hands:
            # 1) Inner selection: best (data_cfg, model) on outer-train
            best = None
            best_score = -1.0

            for dcfg in DATA_CFGS:
                if dcfg not in feature_cache:
                    feature_cache[dcfg] = build_feature_table(meta=meta, data_cfg=dcfg)

                feat_df = feature_cache[dcfg]

                for model_name in TEST_MODELS["supervised"]:
                    score = inner_cv_score(
                        feat_df,
                        subjects_train_outer=outer_train_sub,
                        hand=hand,
                        model_name=model_name,
                        n_splits=inner_splits
                    )

                    if score > best_score:
                        best_score = score
                        best = (dcfg, model_name)

                if best is None:
                    # sollte praktisch nicht passieren, aber robust bleiben
                    results.append({
                        "outer_fold": outer_fold,
                        "hand": hand,
                        "best_model": None,
                        "best_feature_set": None,
                        "best_win": None,
                        "best_step": None,
                        "best_trim": None,
                        "best_min_len": None,
                        "best_inner_score": None,
                        "outer_score": None,
                    })
                    continue

            # 2) Outer evaluation: evaluate best on outer-test
            best_dcfg, best_model = best
            feat_df_best = feature_cache[best_dcfg]
            outer_score, trial_df = eval_holdout(
                feat_df_best,
                train_subjects=outer_train_set,
                test_subjects=outer_test_set,
                hand=hand,
                model_name=best_model,
                return_trials = True
            )

            cm = confusion_matrix(trial_df["true"], trial_df["pred"], labels=list(classes))
            cm_total[hand] += cm

            if plot_per_outer_fold:
                title = (f"NestedCV outer{outer_fold} {hand} | {best_model} | "
                         f"{best_dcfg.feature_set_name} win{best_dcfg.win} step{best_dcfg.step} "
                         f"trim{best_dcfg.trim} minlen{best_dcfg.min_len}")
                out_path = (f"result_plots/nested/outer_folds/"
                            f"{hand}/outer{outer_fold}_{best_model}_{best_dcfg.feature_set_name}_"
                            f"win{best_dcfg.win}_step{best_dcfg.step}.svg")
                plot_cm(cm, classes, out_path, title)

            results.append({
                "outer_fold": outer_fold,
                "hand": hand,
                "best_model": best_model,
                "best_feature_set": best_dcfg.feature_set_name,
                "best_win": best_dcfg.win,
                "best_step": best_dcfg.step,
                "best_trim": best_dcfg.trim,
                "best_min_len": best_dcfg.min_len,
                "best_inner_score": best_score,
                "outer_score": outer_score,
                "n_trials_outer": int(len(trial_df)),
            })
    results_df = pd.DataFrame(results)
    # Gesamt-CM plotten
    for hand in hands:
        out_path = f"result_plots/cm_total_{hand}.svg"
        title = f"NestedCV total CM ({hand}) | outer_splits={outer_splits}"
        plot_cm(cm_total[hand], classes, out_path, title)

    return results_df

def main():
    meta_path = Path("meta.csv")                # bleibt im repo/arbeitspfad

    meta = pd.read_csv(meta_path) # Einlesen von den metadaten
    # Minimale Checks
    for col in ["rel_path", "subject_id", "hand"]: #Kontrolle ob rel_path, subject_id und hand existiert
        if col not in meta.columns:
            raise ValueError(f"meta.csv missing column: {col}")

    ''' this is for now not used
    model_list = []
    for model in TEST_MODELS["supervised"]:  # this is only tmp I have to get another loop with unsupervised and ANN
        model_list.append(ModelConfig(model)) # TODO ACHTUNUG DAS HIER MUSS NOCH GEÄNDERT WERDEN UND ALLE ANDERE FUNKTIONEN
        # model_type="supervised", # TODO after I implemented more models this should be used
    '''

    for params in PARAM_GRID:
        for fs_name, fs in FEATURE_SET_LIBRARY.items():
            DATA_CFGS.append(DataConfig(
                trim= params["trim"],
                min_len= params["min_len"],
                win= params["win"],
                step= params["step"],
                feature_set_name = fs_name,
                time_feature_names = tuple(fs["time"]),
                freq_feature_names = tuple(fs["freq"]),
            ))

    df_nested = nested_cv(meta, outer_splits=5, inner_splits=4, plot_per_outer_fold=False)
    df_nested.to_csv("results_nested.csv", index=False)

    #zusammenfassen
    df_nested_summary = (df_nested
                         .dropna(subset=["outer_score"])
                         .groupby(["hand"])["outer_score"]
                         .agg(["mean", "std", "count"])
                         .reset_index())
    df_nested_summary.to_csv("results_nested_summary.csv", index=False)

if __name__ == "__main__":
    main()