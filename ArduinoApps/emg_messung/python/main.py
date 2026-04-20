import time
from arduino.app_utils import App
from arduino.app_utils import Bridge
from arduino.app_utils import Leds # let the LED blink so we know something is happening
import csv

NEXT_MEASUREMENT = True
Werte_Liste = list()

def envlope_read(finger: int,sensor,envlope: int):
    global NEXT_MEASUREMENT
    global Werte_Liste
    #print(envlope)
    Werte_Liste.append({"Aktueller Finger": finger,"sensor":sensor, "Wert": envlope})
    if finger == 4: # Wenn Finger dem Daumen entspricht --> aus dem Sketch entspricht, die Nummerierung einem enum vom kleinem Finger (0) zum Daumen (4)
        NEXT_MEASUREMENT = True

def messung_speichern(werteVorhanden: bool):
    global NEXT_MEASUREMENT
    global filename
    global Werte_Liste
    if werteVorhanden:
        if NEXT_MEASUREMENT:
            measurement_number = get_next_measurement_number()
            filename = f"Messung_{measurement_number}.csv"
            with open("python/messdaten/last_measurement.txt", "w") as f:
                f.write(str(measurement_number))
            NEXT_MEASUREMENT = False
        
        with open(f'python/messdaten/{filename}', mode='w', encoding='utf-8', newline='') as file:
            fieldnames = Werte_Liste[0].keys()    
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(Werte_Liste)
        Bridge.notify("hochzaehlenFinger")

def get_next_measurement_number():
    """Liest die letzte Messnummer aus der Datei und erhöht sie um 1."""
    try:
        with open("python/messdaten/last_measurement.txt", "r") as f:
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