import pandas as pd
import numpy as np
from scipy.fft import rfft
from pathlib import Path
import tsfel

from auswertung_features.parameterraum import DataConfig
from auswertung_features.features import FEATURES_TIME, FEATURES_FREQ
from ANN.loso_windowed_blockfeat import block_to_windows_postpad

LABEL_COL = "Aktueller Finger"
TIME_COL = "timestamp_ms"
SENSORS = ["sensor_0", "sensor_1", "sensor_2", "sensor_3"]

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
    #df = df.sort_values(TIME_COL).reset_index(drop=True)
    return df

def split_into_label_blocks(df: pd.DataFrame, trim: int = 0, min_len: int = 0) -> list[tuple[np.ndarray, int]]:
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

        if X.shape[0] < min_len != 0: # wenn min_len 300 ist dann werden alle Messungen unter 600ms verworfen
            continue

        trials.append((X, y))  #zurück in die Liste packen

    return trials

def build_feature_table(meta: pd.DataFrame, data_cfg: DataConfig, tsfel_cfg = None) -> pd.DataFrame:
    """
    :param meta: meta.csv mit der Übersicht der Messungen und Probanden
    :param data_cfg: Alle Daten, die ausprobiert werden sollen
    :param tsfel_cfg: Nur genutzt, wenn feature_set_name "tsfel" entspricht, um die Domäne von TSFEL festzulegen
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
            if data_cfg.feature_set_name == "tsfel" or data_cfg.feature_set_name == "default_tsfel":
                X = block_to_windows_postpad(X, T=2000, stride=2000)
                win_dicts = tsfel_window_features_named(X[0], cfg=data_cfg, tsfel_cfg=tsfel_cfg, fs=500)

            else:
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

def tsfel_window_features_named(X: np.ndarray, cfg, tsfel_cfg, fs=500) -> list[dict]:
    """
    X: (N, n_sensors)
    returns: list of dicts, one dict per window, same windowing as window_features_named
    """
    N, n_sensors = X.shape
    out = []

    colnames = [f"s{si}" for si in range(n_sensors)]

    if cfg.win == 0:
        feats_df = tsfel.time_series_features_extractor(tsfel_cfg, X, fs=fs)
        feats = feats_df.iloc[0].to_dict()
        out.append(feats)
        return out

    for start in range(0, N - cfg.win + 1, cfg.step):
        w = X[start:start + cfg.win]

        # TSFEL erwartet DataFrame/Series; DataFrame ist am robustesten
        w_df = pd.DataFrame(w, columns=colnames)

        feats_df = tsfel.time_series_features_extractor(
            tsfel_cfg,
            w_df,
            fs=fs,
        )
        # feats_df hat genau 1 Zeile
        feats = feats_df.iloc[0].to_dict()

        # optional: Prefix, um TSFEL-Features von eigenen zu trennen
        #feats = {f"ts_{k}": float(v) for k, v in feats.items()}

        out.append(feats)

    return out
