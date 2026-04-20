import time
from arduino.app_utils import App
from arduino.app_utils import Bridge
from arduino.app_utils import Leds # let the LED blink so we know something is happening
import csv

MESSUNG_BEENDET = False

Werte_Liste = list()

def envlope_read(finger: int,sensor,envlope: int):
    #print(envlope)
    Werte_Liste.append({"Aktueller Finger": finger,"sensor":sensor, "Wert": envlope})

def messung_speichern(werteVorhanden: bool):
    if werteVorhanden:
        measurement_number = get_next_measurement_number()
        filename = f"Messung_{measurement_number}.csv"
        with open('test.csv', mode='w', encoding='utf-8', newline='') as file:
            fieldnames = Werte_Liste[0].keys()    
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(Werte_Liste)
        Bridge.notify("hochzaehlenFinger")

def get_next_measurement_number():
    """Liest die letzte Messnummer aus der Datei und erhöht sie um 1."""
    try:
        with open("last_measurement.txt", "r") as f:
            last_number = int(f.read().strip())
    except FileNotFoundError:
        last_number = 0
    except ValueError:
        print("Fehler: 'last_measurement.txt' enthält keine gültige Zahl. Starte bei 1.")
        last_number = 0
    return last_number + 1
                    
def loop():
    # Blink LED 1 in red
    # Turn on the LED red segment(1, 0, 0)
    Leds.set_led1_color(1,0,0)
    time.sleep(1)   
    
    # Turn off the LED (0, 0, 0)
    Leds.set_led1_color(0,0,0)
    time.sleep(1)

Bridge.provide("envlope_read", envlope_read)
Bridge.provide("messung_speichern",messung_speichern)
App.run(user_loop=loop)