from arduino.app_utils import App, Bridge, Leds
import time
import pandas as pd
import numpy as np

from features import building_feature, block_to_win
from messung import parse_emg_frame, DATA_DEBUG
from model import load_model, predict_block_from_windows


TIMING_DEBUG = False # used to measure the time to get one frame
dict_time_data = {"sensor_0":[], "sensor_1":[], "sensor_2":[], "sensor_3":[]}
is_recording = False
prediction = None

def start_stop_recording():
    global is_recording, dict_time_data, prediction
    
    is_recording = not is_recording

    if is_recording:       
        Leds.set_led1_color(0, 1, 0)
        dict_time_data = {"sensor_0":[], "sensor_1":[], "sensor_2":[], "sensor_3":[]} # clean dict
    else:
        Leds.set_led1_color(1, 0, 0)
        df_time_data = pd.DataFrame(dict_time_data)
        df_feature = building_feature(df_time_data)
        X_ts = block_to_win(df_time_data, T=500,stride=250) # window length 500 samples and stride 250. On these numbers were the model trained
        prediction = predict_block_from_windows(X_ts, df_feature)


def user_loop():
    global is_recording, prediction
    if is_recording:
        try:
            #Datenblock vom MCU holen
            if TIMING_DEBUG:
                start = time.time()
            frame = Bridge.call("get_emg_frame")
            if TIMING_DEBUG:
                end = time.time()
                dt_get_emg_frame = end - start
                print(f"Getting emg frame needed: {dt_get_emg_frame} s") 
            if frame:
                if TIMING_DEBUG:
                    start = time.time()
                values = parse_emg_frame(bytes(frame))
                if values is not None:
                     for (ts, v1, v2, v3, v4) in values:
                        dict_time_data["sensor_0"].append(v1)
                        dict_time_data["sensor_1"].append(v2)
                        dict_time_data["sensor_2"].append(v3)
                        dict_time_data["sensor_3"].append(v4)
               
                if TIMING_DEBUG:
                    end = time.time()
                    dt_parsing_emg_frame = end - start
                    print(f"Parsing Frame needed: {dt_parsing_emg_frame} s")
                    print(f"Time of both: {dt_get_emg_frame + dt_parsing_emg_frame}")
        except Exception as e:
            print(f"Fehler bei Bridge.call: {e}")

    if prediction is not None:
        Bridge.notify("draw_finger", prediction)
        prediction = None
        time.sleep(3)
        Bridge.notify("draw_ready")
    time.sleep(0.01) # Alle 10ms nach neuen Daten fragen

if __name__ == "__main__":
    Bridge.provide("start_stop", start_stop_recording)
    load_model()
    is_recording = False
    Bridge.notify("draw_ready")
    App.run(user_loop=user_loop)