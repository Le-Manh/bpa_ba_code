from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from models import MODELS_SUPERVISED
from features import FEATURES_TIME, FEATURES_FREQ
from parameterraum import FEATURE_SETS, TEST_MODELS

from sklearn.model_selection import LeaveOneGroupOut, LeavePGroupsOut

from sklearn.metrics import confusion_matrix, classification_report, ConfusionMatrixDisplay, f1_score, accuracy_score

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

def build_feature_table(meta: pd.DataFrame, trim: int = 50, min_len: int = 300,
                        win: int = 100, step: int = 50) -> pd.DataFrame:
    """
    :param meta: meta.csv mit der Übersicht der Messungen und Probanden
    :param trim: Wie viel vor und hinter dem Trial getrimmt werden soll
    :param min_len: minimaler Länge des Trials
    :param win: Länge des Windows
    :param step: Schritt der feature extraction
    :return: dataframe mit den extraktions features
    """
    rows = []
    for i, r in meta.iterrows(): # über die Tabelle iterieren
        csv_path = r["rel_path"]
        df = load_session(csv_path) # csv laden + check ob die wichtigen spalten existieren

        #Error Handling für leere dfs
        if df is None:
            continue

        blocks = split_into_label_blocks(df, trim=trim, min_len=min_len)

        # Check: idealerweise genau 5 Blöcke (0..4)
        # Wenn nicht, loggen (nicht zwingend skippen).
        labels_found = [y for (_, y) in blocks]
        if len(blocks) != 5 or sorted(set(labels_found)) != [0,1,2,3,4]:
            print(f"[WARN] {csv_path}: found blocks={len(blocks)}, labels={labels_found}")

        for trial_id, (X, y) in enumerate(blocks):
            F = window_features(X,FEATURE_SETS["time"],FEATURE_SETS["freq"], win=win, step=step)
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

def run_loso(feature_df: pd.DataFrame, hand: str, model: str):
    df = feature_df[feature_df["hand"] == hand].copy() # Extraction of the hand (l or r)
    if df.empty:
        print(f"No data for hand={hand}")
        return

    X = df[[c for c in df.columns if c.startswith("f")]].to_numpy(dtype=np.float32) # suche nach den feature columns. Starten mit "f"
    y = df["label"].to_numpy(dtype=int) # suche nach blocklabel
    groups = df["subject_id"].to_numpy()  # gruppierung nach der subject_id

    logo = LeavePGroupsOut(2) # Provides train/test split by letting one out of the groups
    model = MODELS_SUPERVISED[model]

    # window-level predictions sammeln
    preds = np.empty_like(y) # Allocation of memory, values in preds are arbitrary
    for train_idx, test_idx in logo.split(X, y, groups=groups): # using logo to split and train model
        model.fit(X[train_idx], y[train_idx])
        preds[test_idx] = model.predict(X[test_idx]) # look at the test_idx

    df_pred = df[["subject_id", "session", "trial_id", "label"]].copy()
    df_pred["pred"] = preds # adding the prediction in a new df

    # trial-level voting
    trial_df = trial_level_vote(df_pred)  # majority vote der sliding windows

    labels = [0,1,2,3,4]
    cm = confusion_matrix(trial_df["true"], trial_df["pred"], labels=labels)
    print(f"\n=== HAND {hand}: Trial-level Confusion Matrix (labels 0..4) ===")
    print(cm)

    print(f"\n=== HAND {hand}: Trial-level report ===") # precision ist wie oft richtig, recall sensitivität wie viele der richtigen wenn wirklich richtig, F1 Mittelwert-Kompromiss aus precision & recall
    print(classification_report(trial_df["true"], trial_df["pred"], labels=labels, digits=3))

    showAccuracyAndCM(trial_df["true"], trial_df["pred"], labels)

    # Fokus: klein (0) vs ring (1)
    mask01 = trial_df["true"].isin([0,1])
    if mask01.any():
        cm01 = confusion_matrix(trial_df.loc[mask01,"true"], trial_df.loc[mask01,"pred"], labels=[0,1])
        print(f"\n=== HAND {hand}: Fokus 0<->1 (klein<->ring) ===")
        print(cm01)

def showAccuracyAndCM(fingerLabelArray, predictedLabels, classes):
    print("accuracy_score:  " + str(accuracy_score(fingerLabelArray, predictedLabels)))
    print("F1-Score: " + str(f1_score(fingerLabelArray, predictedLabels, average=None, zero_division=0)))
    #print(classification_report(fingerLabelArray, predictedLabels, zero_division=0))
    cm2 = confusion_matrix(fingerLabelArray, predictedLabels, labels=classes)
    disp2 = ConfusionMatrixDisplay(confusion_matrix=cm2, display_labels=classes)
    disp2.plot()
    #plt.show()

def main():

    meta_path = Path("meta.csv")                # bleibt im repo/arbeitspfad

    meta = pd.read_csv(meta_path) # Einlesen von den metadaten
    # Minimale Checks
    for col in ["rel_path", "subject_id", "hand"]: #Kontrolle ob rel_path, subject_id und hand existiert
        if col not in meta.columns:
            raise ValueError(f"meta.csv missing column: {col}")

    # Features bauen
    feat_df = build_feature_table(
        meta=meta,
        trim=50,
        min_len=300,
        win=300,
        step=100
    )

    print("Feature table shape:", feat_df.shape)
    print("Subjects:", feat_df["subject_id"].nunique(), "Sessions:", feat_df["session"].nunique())

    # LOSO getrennt für l und r
    # gleichzeitiger Test mehrerer supervised Modelle
    for model in TEST_MODELS["supervised"]:
        run_loso(feat_df, hand="l",model=model)
        run_loso(feat_df, hand="r",model=model)

if __name__ == "__main__":
    main()