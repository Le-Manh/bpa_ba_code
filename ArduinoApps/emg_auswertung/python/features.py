import tsfel
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np

TSFEL_CFG = tsfel.get_features_by_domain() # TSFEL_CFG is global

def building_feature(data: pd.DataFrame, fs:int = 500) -> pd.DataFrame:
    """
    build the Featuretable with the data. TSFEL can also work with Series and ndarray
    :param data: TimeSeries of the data
    :param fs: frequency of the signal
    :return: DataFrame with extracted data
    """
    global TSFEL_CFG
    X_feat = np.asarray(data, dtype=np.float32)
    feats_df = tsfel.time_series_features_extractor(TSFEL_CFG, X_feat, fs=fs)
    
    return feats_df

def block_to_windows_postpad(x_ts: np.ndarray, T: int, stride: int):
    """
    x_ts: (L,4)
    Returns list of windows (T,4).
    padding style:
      - if L < T: post-pad with zeros
      - if L >= T: sliding windows of length T
      - last window is forced to include the end of the block
    """
    x_ts = np.asarray(x_ts, np.float32)
    L = x_ts.shape[0]

    if L <= T:
        w = np.zeros((T, 4), np.float32)
        w[:L, :] = x_ts
        return [w]

    wins = []
    for start in range(0, L - T + 1, stride):
        wins.append(x_ts[start:start + T, :])

    # force last window to not "miss" the end
    last_start = L - T
    if (last_start % stride) != 0:
        wins.append(x_ts[last_start:last_start + T, :])

    return wins

def block_to_win(x_ts: np.ndarray, T: int, stride:int):

    X_ts_list =[]
    windows = block_to_windows_postpad(x_ts, T, stride)

    for w in windows:
        X_ts_list.append(w)

    X_ts = np.stack(X_ts_list, axis=0).astype(np.float32)

    return X_ts