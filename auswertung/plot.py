import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

csv_data = pd.read_csv("../ArduinoApps/emg_messung/python/messdaten/Test.csv")
splitted_data = list()

for i in range(4):
    splitted_data.append(csv_data[csv_data['sensor'] == i][['Aktueller Finger','Wert']]) #split Messung per sensor






print