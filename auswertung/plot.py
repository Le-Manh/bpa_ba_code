import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

path_messdaten = "../ArduinoApps/emg_messung/python/messdaten/"
name_data = "debug.csv"

csv_data = pd.read_csv(path_messdaten+name_data)
splitted_data = list()
fingerTypes = ["kleiner Finger","Ringfinger","Mittelfinger","Zeigefinger","Daumen"]
value_types = ["wert_raw", "werte_gefiltert", "Wert", "Offset"]

def drawFingerTypeLabel(ax,df,n):
    for i in range(0,): # For-Schleife über die Finger-Indizes 0...4
        a = df["Aktueller Finger"].to_numpy().searchsorted(i, side='left') # sucht die Position an der i (Fingerindex) in der Spalte "Aktueller Finger" erstmals auftritt, a = Startposition des Fingers i
        b = df["Aktueller Finger"].to_numpy().searchsorted(i, side='right') # sucht die Position an der i (Fingerindex) in der Spalte "Aktueller Finger" hinter dem letzten i-Fingerindex-Wert, b = Endposition des Fingers i
        ax.axvline(x = a, alpha = 0.5, color = "black", linestyle = "--") # zeichnet eine gestrichelte Linie an der Stelle a
        ax.text((b+a)/2, np.min(df[value_types[n]]), fingerTypes[i],horizontalalignment='center',verticalalignment='top') # Schreibt den Finger-Namen an der x-Stelle (a+b)/2, also auf der Hälfte, und y-Stelle am unteren Rand des Diagramms und zentriert den Begriff an der Stelle
        if(b == len(df["Aktueller Finger"])): # Prüfen, ob b gleich der Länge aller Daten des DataFrames ist
            ax.axvline(x = b, alpha = 0.5, color = "black", linestyle = "--") # Wenn ja, letzte Schwarze Linies

def draw_plot(df_data: pd.DataFrame, sensor: int, name: str="") -> tuple:
    fig, axes = plt.subplots(nrows=2, ncols=2,figsize=(20,10))

    ax = axes.ravel()
    for n in range(len(value_types)):
        ax[n].plot(df_data[value_types[n]], label="Sensor " + str(sensor))
        ax[n].legend()
        ax[n].set_title('Datensatz '+ name + " " + value_types[n])
        ax[n].set_xlabel('Samples')
        ax[n].set_ylabel('EMG-Amplitude')

    return fig,ax

for i in range(4): # die 4 steht für Anzahl sensoren
    splitted_data.append(csv_data[csv_data['sensor'] == i][['Aktueller Finger',"wert_raw","werte_gefiltert",'Wert',"Offset"]].reset_index()) #split Messung per sensor und reset den Index

    fig,ax = draw_plot(splitted_data[i], sensor=i, name=f"{i}")
    for n in range(len(value_types)):
        drawFingerTypeLabel(ax[n], splitted_data[i],n)

    #plt.tight_layout()

    fig.savefig(f"plots/plot_{name_data}_sensor{i}.svg", format='svg')
    plt.close(fig)