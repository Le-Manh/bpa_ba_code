import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay
import os

def plot_cm(cm: np.ndarray, classes, out_path: str, title: str):
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=classes)
    disp.plot()
    disp.ax_.set_title(title)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    disp.figure_.savefig(out_path, format="svg")
    plt.close(disp.figure_)
