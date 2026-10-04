import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from sklearn.metrics import ConfusionMatrixDisplay
import numpy as np
import pandas as pd
import seaborn as sns

def split_violin_plot_choice(df: pd.DataFrame, value: str, title: str | None = None) -> Figure:
    """
    plots a split violin for the Values Accuracy and Macro F1.

    Parameters:
    ----------
    df : pd.DataFrame
        Dataframe with the data which is used to plot the violin plot
        It expects the columns: "val_acc", "val_macro_f1" and the column on which the violin plot should happen
    value : str
        This values is the name of the column on which the violin plot is plotted
    title : str | None, default = None
        the title for the violin plot is optional

    Returns:
    --------
    Figure
    """
    # ---------- Violinplots für AccuracyMean und MacroF1Mean ----------
    df_long = df[["val_acc", "val_macro_f1", value]].rename(
        columns={"val_acc": "Accuracy", "val_macro_f1": "Macro F1"}
        ).melt(id_vars= [value],var_name="Metric", value_name="Value")

    order_hue = ["Accuracy", "Macro F1"]

    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(8,6))

    sns.violinplot(
        data=df_long,
        x=value, y="Value",
        hue="Metric",
        hue_order=order_hue,
        split=True,          # links/rechts gesplittet
        inner="box",
        cut=0,
        gap= 0.05,
        linewidth=1,
        palette="pastel"
    )

    sns.stripplot(
        data=df_long,
        x=value, y="Value",
        hue="Metric",
        hue_order=order_hue,
        dodge=True,          # trennt die Punkte links/rechts
        size=4
    )

    plt.ylim(0, 1)
    plt.xlabel("")
    plt.ylabel("metric score")
    if title is not None:
        plt.title(title)

    # doppelte Legendeneinträge entfernen (weil violinplot + stripplot beide legend machen)
    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(handles[:2], labels[:2], title="Metric", loc="lower left")

    return fig

def cm_to_plot(cm: np.ndarray, title=None)-> Figure:
    """
    plots the confusion matrix for the 5 movement classes based on a cm

    Parameters:
    ----------
    cm : np.ndarray
        The confusion matrix
    title : str | None, default = None
        the title for the confusion matrix, optional

    Returns:
    --------
    Figure
    """
    classes = np.array(["kleiner Finger", "Ringfinger", "Mittelfinger", "Zeigefinger", "Daumen"])

    # Figure + Grid: links Matrix, rechts Colorbar (schmal)
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot()

    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=classes)

    disp.plot(ax=ax,xticks_rotation=30,)

    if title:
        ax.set_title(title)

    return fig