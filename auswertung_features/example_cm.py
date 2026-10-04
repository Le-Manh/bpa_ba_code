import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay
import matplotlib.patheffects as pe

cm = np.array([[42,8],[5,45]])

disp = ConfusionMatrixDisplay(confusion_matrix=cm,display_labels=["Class k","Class not k"])

fig, ax = plt.subplots(figsize=(4.5,4))
disp.plot(ax=ax, colorbar=True)

cell_tags = np.array([["TP", "FN"], ["FP", "TN"]])

for i in range(2):
    for j in range(2):
        t = ax.text(j, i-0.18, cell_tags[i,j],
                ha="center", va="center",
                fontsize=11, fontweight="bold", color="white")
        t.set_path_effects([pe.withStroke(linewidth=4, foreground="black")])

plt.tight_layout()
fig.savefig("Beispiel_cm.svg", transparent=True)