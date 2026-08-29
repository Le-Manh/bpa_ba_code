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
    feats_df = tsfel.time_series_features_extractor(TSFEL_CFG, data, fs=fs)
    feats_df.to_csv("tsfel.csv")
    
    return feats_df