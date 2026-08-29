from arduino.app_utils import App, Bridge, Leds
import time
import pandas as pd
import numpy as np

from features import building_feature
from messung import dict_finger, current_finger_state, open_new_csv, parse_emg_frame, DATA_DEBUG
from model import load_model, get_prediction


TIMING_DEBUG = False # used to measure the time to get one frame
dict_time_data = {"sensor_0":[], "sensor_1":[], "sensor_2":[], "sensor_3":[]}
is_recording = False
handState = True

def start_stop_recording(whichHand: bool):
    global is_recording, dict_time_data, handState
    handState = whichHand
    if handState: # LED Feedback zur hand. blue is left and nothing is right
        Leds.set_led2_color(0,0,0)
    else:
        Leds.set_led2_color(0,0,1)

    is_recording = not is_recording

    if is_recording:       
        Leds.set_led1_color(0, 1, 0)
        dict_time_data = {"sensor_0":[], "sensor_1":[], "sensor_2":[], "sensor_3":[]} # clean dict
    else:
        Leds.set_led1_color(1, 0, 0)
        df_time_data = pd.DataFrame(dict_time_data)
        df_feature = building_feature(df_time_data)
        prediction = get_prediction(df_time_data, df_feature)
        print(prediction)
        


def user_loop():
    global is_recording
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

    time.sleep(0.01) # Alle 10ms nach neuen Daten fragen

if __name__ == "__main__":
    Bridge.provide("start_stop", start_stop_recording)
    load_model()
    is_recording = False
    handState = True
    App.run(user_loop=user_loop)