import matplotlib.pyplot as plt
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


from auswertung_features.build_features import build_feature_table
from parameterraum import DataConfig

sensor_list = ["sensor_0", "sensor_1", "sensor_2", "sensor_3"]

meta = pd.read_csv('meta.csv')

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

b_TSFEL = False
df = build_feature_table(meta, cfg, b_TSFEL= b_TSFEL)

df.iloc[:,7:] = StandardScaler().fit_transform(df.iloc[:,7:])
pca = PCA(n_components=2)
df_2D_right = pca.fit_transform(df[df["hand"] == "r"].iloc[:, 7:])

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
    save_name = "scatter_plot_2d_PCA_TSFEL_r.svg"
else:
    save_name = "scatter_plot_2d_PCA_r.svg"
fig.savefig(save_name)