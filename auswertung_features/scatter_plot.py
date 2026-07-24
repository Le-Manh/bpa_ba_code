from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from narwhals import String
from sklearn.decomposition import PCA
import seaborn as sns
from seaborn.objects import Plot

from auswertung_features.build_features import build_feature_table
from build_features import load_session, split_into_label_blocks
from parameterraum import DataConfig

sensor_list = ["sensor_0", "sensor_1", "sensor_2", "sensor_3"]

meta = pd.read_csv('meta.csv')

cfg = DataConfig(
    trim=0,
    min_len=0,
    win = 300,
    step = 25,
    feature_set_name= "time+freq",
    time_feature_names =("rms",
             "wl",
             "p",
             "min",
             "max",
             "mean",
             "std",
             "var",
             "mav",
             "peak",
             "ptp",
             "crest",
             "skew",
             "kurtosis",) ,
    freq_feature_names = ("max_freq",
             "sum_freq",
             "mean_freq",
             "var_freq",
             "skew_freq",
             "kurtosis_freq",
             ),
)

df = build_feature_table(meta, cfg)

print(df)


pairplot = sns.pairplot(
    df,
    vars=sensor_list,
    hue="Aktueller Finger",
    )


print(index)