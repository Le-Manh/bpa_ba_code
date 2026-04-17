import time
from arduino.app_utils import App
from arduino.app_utils import Bridge
from arduino.app_utils import Leds # let the LED blink so we know something is happening
import csv

MESSUNG_BEENDET = False
MESSUNG_STATE = False
Werte_Liste = list()

def envlope_read(finger: int,envlope: int):
    print(envlope)
    Werte_Liste.append({"Aktueller Finger": finger, "Wert": envlope})

def messung(state: bool):
    MESSUNG_STATE = state

def messung_speichern(werteVorhanden: bool):
    if werteVorhanden:
        with open('test.csv', mode='w', encoding='utf-8', newline='') as file:
            fieldnames = ["Aktueller Finger", "Wert"]    
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(Werte_Liste)
        Bridge.notify("hochzaehlenFinger")

                    
def loop():
    # Blink LED 1 in red
    # Turn on the LED red segment(1, 0, 0)
    Leds.set_led1_color(1,0,0)
    time.sleep(1)   
    
    # Turn off the LED (0, 0, 0)
    Leds.set_led1_color(0,0,0)
    time.sleep(1)

Bridge.provide("messung",messung)
Bridge.provide("envlope_read", envlope_read)
Bridge.provide("messung_speichern",messung_speichern)
App.run(user_loop=loop)