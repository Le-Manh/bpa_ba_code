from arduino.app_utils import App, Bridge, Leds
import time

from features import building_feature
from messung import dict_finger, current_finger_state, open_new_csv, parse_emg_frame, DATA_DEBUG

TIMING_DEBUG = False # used to measure the time to get one frame
dict_time_data = {"sensor_0":[], "sensor_1":[], "sensor_2":[], "sensor_3":[]}

def start_stop_recording(whichHand: bool):
    global is_recording, current_finger_state, handState
    handState = whichHand
    if handState: # LED Feedback zur hand. blue is left and nothing is right
        Leds.set_led2_color(0,0,0)
    else:
        Leds.set_led2_color(0,0,1)

    is_recording = not is_recording

    if is_recording:
        if current_finger_state == dict_finger["littleFinger"]:
            if DATA_DEBUG:
                print("Aufnahme gestartet...")
            open_new_csv()
        Leds.set_led1_color(0, 1, 0)
    else:
        Leds.set_led1_color(1, 0, 0)
        if current_finger_state == dict_finger["thumb"]:
            if DATA_DEBUG:
                print("Aufnahme gestoppt. csv wird geschlossen")
            close_csv()
            current_finger_state = dict_finger["littleFinger"]
            Leds.set_led1_color(0, 0, 0)
        else:
            current_finger_state += 1
    if DATA_DEBUG:
        print(f"der derzeitige Finger ist: Finger {current_finger_state}") 


def user_loop():
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
                    for i, value in enumerate(values):
                        dict_time_data[f"sensor{i}"].append(value)
                
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
    
    App.run(user_loop=user_loop)