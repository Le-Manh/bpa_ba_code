import matplotlib.pyplot as plt
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

from auswertung_features.build_features import build_feature_table
from parameterraum import DataConfig

sensor_list = ["sensor_0", "sensor_1", "sensor_2", "sensor_3"]

meta = pd.read_csv('meta.csv')

# choose to use LDA or PCA
str_dim_red = "LDA"

# choose to use TSFEL
b_TSFEL = False

cfg = DataConfig(
    trim=0,
    min_len=0,
    win = 500,
    step = 50,
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


df = build_feature_table(meta, cfg, b_TSFEL= b_TSFEL)

df.iloc[:,6:] = StandardScaler().fit_transform(df.iloc[:,6:])
if str_dim_red == "LDA":
    lda = LinearDiscriminantAnalysis()
    df_2D_right = lda.fit_transform(df[df["hand"] == "r"].iloc[:, 6:], df[df["hand"] == "r"]["label"])
else:
    pca = PCA(n_components=2)
    str_dim_red = "PCA"
    df_2D_right = pca.fit_transform(df[df["hand"] == "r"].iloc[:, 6:])

fig = plt.figure()
ax = fig.add_subplot()

scatter = ax.scatter(df_2D_right[:,0],df_2D_right[:,1],c=df[df["hand"]=="r"]["label"].tolist())

legend1 = ax.legend(
    scatter.legend_elements()[0],
    ["Lf","Rf","Mf","If","th"],
    loc="upper right",
    title="Classes",
)
ax.add_artist(legend1)

plt.legend()
if b_TSFEL:
    save_name = f"scatter_plot_2d_{str_dim_red}_TSFEL_r.svg"
else:
    save_name = f"scatter_plot_2d_{str_dim_red}_r.svg"
fig.savefig(save_name)