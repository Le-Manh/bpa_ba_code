from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import json

from models import MODELS_SUPERVISED
from features import FEATURES_TIME, FEATURES_FREQ
from parameterraum import FEATURE_SETS, TEST_MODELS, PARAM_GRID, model_config

from sklearn.model_selection import LeaveOneGroupOut, LeavePGroupsOut
from sklearn.base import clone
from sklearn.metrics import (confusion_matrix, classification_report, ConfusionMatrixDisplay,
                             f1_score, accuracy_score, balanced_accuracy_score,
                             matthews_corrcoef, cohen_kappa_score
                             )

from scipy.fft import rfft

LABEL_COL = "Aktueller Finger"
TIME_COL = "timestamp_ms"
SENSORS = ["sensor_0", "sensor_1", "sensor_2", "sensor_3"]

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

def window_features(X: np.ndarray, feature_name_time: list,feature_name_freq: list, win: int = 100, step: int = 50, eps: float = 1e-8) -> np.ndarray:
    """
    X: (N,4) float32
    returns: (n_windows, n_features)
    Features: RMS(4) + WL(4) + p(4) + ratio_ext_flex(1) = 13
    """
    feats = []

    N = X.shape[0]
    for start in range(0, N - win + 1, step): # loop durch alle Werte. Start 0, Ende alle N Werte ohne den letzte win, wenn step größer ist als das letzte win dann wird komplett übersprungen
        w = X[start:start + win] # window extrahieren
        ft = rfft(w, axis=0)
        s = (np.abs(ft) ** 2) / w.shape[0]

        time_parts = [FEATURES_TIME[name](w, eps=eps) for name in feature_name_time]
        freq_parts = [FEATURES_FREQ[name](s, eps=eps) for name in feature_name_freq]

        f = np.concatenate(time_parts+freq_parts, axis=0)
        feats.append(f)

    if not feats:
        return np.zeros((0, 13), dtype=np.float32) # falls keine Features 0 hinzufügen

    return np.vstack(feats).astype(np.float32)  # rebuilded Array from a list as a vertical Array (1,N)

def build_feature_table(meta: pd.DataFrame,model_cfg: model_config) -> pd.DataFrame:
    """
    :param meta: meta.csv mit der Übersicht der Messungen und Probanden
    :param model_cfg: Alle Daten die ausprobeirt werden sollen
    :return: dataframe mit den extractions features
    """
    rows = []
    for i, r in meta.iterrows(): # über die Tabelle iterieren
        csv_path = r["rel_path"]
        df = load_session(csv_path) # csv laden + check ob die wichtigen spalten existieren

        #Error Handling für leere dfs
        if df is None:
            continue

        blocks = split_into_label_blocks(df, trim=model_cfg.trim, min_len=model_cfg.min_len)

        # Check: idealerweise genau 5 Blöcke (0..4)
        # Wenn nicht, loggen (nicht zwingend skippen).
        labels_found = [y for (_, y) in blocks]
        if len(blocks) != 5 or sorted(set(labels_found)) != [0,1,2,3,4]:
            print(f"[WARN] {csv_path}: found blocks={len(blocks)}, labels={labels_found}")

        for trial_id, (X, y) in enumerate(blocks):
            F = window_features(X,FEATURE_SETS["time"],FEATURE_SETS["freq"], win=model_cfg.win, step=model_cfg.step)
            # Falls nach Fensterung nix übrig bleibt -> skip
            if F.shape[0] == 0:
                continue

            for widx in range(F.shape[0]): # neubau des Dataframe mit features
                feat = F[widx]
                rows.append({
                    "subject_id": str(r["subject_id"]),
                    "hand": str(r["hand"]),
                    "session": csv_path,
                    "trial_id": trial_id,
                    "label": y, # Klassenlabel
                    "widx": widx,
                    **{f"f{j}": float(feat[j]) for j in range(feat.shape[0])}
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

def run_loso(feature_df: pd.DataFrame, hand: str, model_cfg: model_config):
    df = feature_df[feature_df["hand"] == hand].copy() # Extraction of the hand (l or r)
    if df.empty:
        print(f"No data for hand={hand}")
        return

    X = df[[c for c in df.columns if c.startswith("f")]].to_numpy(dtype=np.float32) # suche nach den feature columns. Starten mit "f"
    y = df["label"].to_numpy(dtype=int) # suche nach blocklabel
    groups = df["subject_id"].to_numpy()  # gruppierung nach der subject_id

    labels = np.sort(df["label"].unique())

    run_id = (
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
        f"{model_cfg.model_name}_{hand}_"
        f"trim{model_cfg.trim}_minlen{model_cfg.min_len}_win{model_cfg.win}_step{model_cfg.step}"
    )

    logo = LeavePGroupsOut(2) # Provides train/test split by letting one out of the groups

    fold_rows = []
    cm_total = None

    # window-level predictions sammeln
    for fold_i, (train_idx, test_idx) in enumerate(logo.split(X, y, groups=groups)):
        model = MODELS_SUPERVISED[model_cfg.model_name]()  # pro Fold neu!
        model.fit(X[train_idx], y[train_idx])

        y_pred_win = model.predict(X[test_idx])

        df_pred_fold = df.iloc[test_idx][["subject_id", "session", "trial_id", "label"]].copy()
        df_pred_fold["pred"] = y_pred_win

        trial_df_fold = trial_level_vote(df_pred_fold)  # -> true, pred

        metrics = eval_trial_fold(trial_df_fold, classes=labels)
        cm_total = metrics["_cm"] if cm_total is None else (cm_total + metrics["_cm"])

        # Meta/Parameter dazu
        metrics.update({
            "run_id": run_id,
            "model_name": model_cfg.model_name,
            "hand": hand,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "level": "trial",
            "fold": int(fold_i),
            "trim": model_cfg.trim,
            "min_len": model_cfg.min_len,
            "win": model_cfg.win,
            "step": model_cfg.step,
        })

        append_row_csv(metrics, "results_folds.csv")
        fold_rows.append(metrics)

    # Summary schreiben
    summary = summarize_folds(fold_rows)
    summary.update({
        "run_id": run_id,
        "model_name": model_cfg.model_name,
        "hand": hand,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "level": "trial",
        "trim": model_cfg.trim,
        "min_len": model_cfg.min_len,
        "win": model_cfg.win,
        "step": model_cfg.step,
        "n_splits": logo.get_n_splits(X, y, groups),
    })
    append_row_csv(summary, "results_summary.csv")

    plot_cm(cm_total, labels, run_id, model_cfg = model_cfg)

def plot_cm(cm, classes, run_id:str, model_cfg: model_config):
    disp2 = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=classes)
    disp2.plot()
    disp2.ax_.set_title(f"Confusion Matrix (CV sum) {model_cfg.model_name}")

    # making sure the subdir exist
    script_dir = os.path.dirname(__file__)
    results_dir = os.path.join(script_dir, f'result_plots/{model_cfg.model_name}')
    if not os.path.isdir(results_dir):
        os.makedirs(results_dir)

    disp2.figure_.savefig(f"result_plots/{model_cfg.model_name}/{run_id}", format="svg")
    plt.close(disp2.figure_)

def eval_trial_fold(trial_df: pd.DataFrame, classes):
    """trial_df hat Spalten: true, pred"""
    y_true = trial_df["true"].to_numpy()
    y_pred = trial_df["pred"].to_numpy()

    cm = confusion_matrix(y_true, y_pred, labels=classes)

    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1_weighted": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "mcc": float(matthews_corrcoef(y_true, y_pred)),
        "kappa": float(cohen_kappa_score(y_true, y_pred)),
        "n_trials": int(len(trial_df)),
        "cm_json": json.dumps(cm.tolist()),
        "_cm": cm,  # intern, nicht in CSV schreiben
    }

def append_row_csv(row: dict, path: str):
    d = dict(row)
    d.pop("_cm", None)
    df = pd.DataFrame([d])
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)

def summarize_folds(fold_rows, keys=("accuracy","balanced_accuracy","f1_macro","f1_weighted","mcc","kappa")):
    out = {}
    for k in keys:
        vals = np.array([r[k] for r in fold_rows], dtype=float)
        out[f"{k}_mean"] = float(vals.mean())
        out[f"{k}_std"]  = float(vals.std(ddof=1)) if len(vals) > 1 else 0.0
    out["n_folds"] = int(len(fold_rows))
    out["n_trials_total"] = int(sum(r["n_trials"] for r in fold_rows))
    return out

def main():

    meta_path = Path("meta.csv")                # bleibt im repo/arbeitspfad

    meta = pd.read_csv(meta_path) # Einlesen von den metadaten
    # Minimale Checks
    for col in ["rel_path", "subject_id", "hand"]: #Kontrolle ob rel_path, subject_id und hand existiert
        if col not in meta.columns:
            raise ValueError(f"meta.csv missing column: {col}")
    # TODO change build_feature_table so it can 1. iterate from PARAM_GRID and 2. give it to run_loso so it can be written in the result.csv

    for model in TEST_MODELS["supervised"]: # this is only tmp I have to get another loop with unsupervised and ANN
        for params in PARAM_GRID:
            model_cfg = model_config(
                model_name=model,
                #model_type="supervised", # TODO after I implemented more models this should be used
                trim= params["trim"],
                min_len= params["min_len"],
                win= params["win"],
                step= params["step"],
                features = FEATURE_SETS,
            )

            # Features bauen
            feat_df = build_feature_table(
            meta=meta,
            model_cfg=model_cfg,
            )

            print("Feature table shape:", feat_df.shape)
            print("Subjects:", feat_df["subject_id"].nunique(), "Sessions:", feat_df["session"].nunique())

            # LOSO getrennt für l und r
            # gleichzeitiger Test mehrerer supervised Modelle

            run_loso(feat_df, hand="l",model_cfg=model_cfg)
            run_loso(feat_df, hand="r",model_cfg=model_cfg)

if __name__ == "__main__":
    main()