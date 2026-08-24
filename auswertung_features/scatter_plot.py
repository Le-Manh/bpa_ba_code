import json

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import tsfel

from build_features import build_feature_table
from parameterraum import DataConfig


def main():
    sensor_list = ["sensor_0", "sensor_1", "sensor_2", "sensor_3"]

    meta = pd.read_csv("meta.csv")

    # choose to use LDA or PCA
    str_dim_red = "LDA"
    str_hand = "r"          # choose the hand

    cfg = DataConfig(
        trim=0,
        min_len=110,
        win=110,
        step=50,
        feature_set_name="tsfel", # allowed are tsfel, time, freq or time+freq
        time_feature_names=(
            "rms","wl","p","min","max","mean","std","var","mav","peak","ptp",
            "crest","skew","kurtosis"
        ), # the list of time and freq features are skipped if tsfel is used --> tsfel_conf is used
        freq_feature_names=(
            "max_freq","sum_freq","mean_freq","var_freq","skew_freq","kurtosis_freq"
        ),
    )

    tsfel_cfg = tsfel.get_features_by_domain(json_path="tsfel_conf.json")

    df = build_feature_table(meta, cfg, tsfel_cfg=tsfel_cfg)

    df.iloc[:, 6:] = StandardScaler().fit_transform(df.iloc[:, 6:])

    if str_dim_red == "LDA":
        lda = LinearDiscriminantAnalysis()
        mask = df["hand"] == str_hand
        df_2D_right = lda.fit_transform(df.loc[mask].iloc[:, 6:], df.loc[mask, "label"])
    else:
        pca = PCA(n_components=2)
        str_dim_red = "PCA"
        mask = df["hand"] == str_hand
        df_2D_right = pca.fit_transform(df.loc[mask].iloc[:, 6:])

    fig = plt.figure()
    ax = fig.add_subplot()

    mask = df["hand"] == str_hand
    scatter = ax.scatter(df_2D_right[:, 0], df_2D_right[:, 1], c=df.loc[mask, "label"].tolist())

    legend1 = ax.legend(
        scatter.legend_elements()[0],
        ["Lf", "Rf", "Mf", "If", "Th"],
        loc="upper right",
        title="Classes",
    )
    ax.add_artist(legend1)

    plt.legend()
    if b_TSFEL:
        save_name = f"result_plots/scatter_plot_2d_{str_dim_red}_TSFEL_{str_hand}_test.svg"
    else:
        save_name = f"result_plots/scatter_plot_2d_{str_dim_red}_{str_hand}.svg"
    fig.savefig(save_name)


if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    main()
