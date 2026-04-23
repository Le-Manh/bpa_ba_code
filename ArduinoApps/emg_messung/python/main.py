import time
from arduino.app_utils import App
from arduino.app_utils import Bridge
from arduino.app_utils import Leds # let the LED blink so we know something is happening
import csv

# globale Variablen, die im gesamten Skripe gleichbleiben
NEXT_MEASUREMENT = True # Hiermit wird getrackt, ob eine neue Datei erstellt werden soll
Werte_Liste = list()

def envlope_read(finger: int,sensor: int,envlope: int):
    """Packt die Daten aus den Sensoren in ein Dict, damit es als csv abgespeichert werden kann"""
    global NEXT_MEASUREMENT # Hiermit wird getrackt, ob eine neue Datei erstellt werden soll
    global Werte_Liste # Unsere Werte in einer Liste
    print(envlope)
    Werte_Liste.append({"Aktueller Finger": finger,"sensor":sensor, "Wert": envlope})
    if finger == 4: # Wenn Finger dem Daumen entspricht --> aus dem Sketch entspricht, die Nummerierung einem enum vom kleinem Finger (0) zum Daumen (4)
        NEXT_MEASUREMENT = True

def messung_speichern(werteVorhanden: bool):
    """Speichert die Messung aus Werte_Liste in eine csv und nummeriert die Messung basierend auf der last_measurement.txt
        Da diese Funktion auch immer von der MCU Seite aufgerufen wird, wird die Variable werteVorhanden übergegeben, um sicherzustellen, dass Werte_Liste auch vollständig ist und gerade nicht beschrieben wird
    """
    global NEXT_MEASUREMENT 
    global filename # Das wird gebraucht, damit beim nächsten Aufruf die Funktion noch weiß, wie die Datei hieß
    global Werte_Liste
    if werteVorhanden:
        if NEXT_MEASUREMENT:
            measurement_number = get_next_measurement_number()
            filename = f"Messung_{measurement_number}.csv"
            with open("python/messdaten/last_measurement.txt", "w") as f:
                f.write(str(measurement_number))
            NEXT_MEASUREMENT = False
            Bridge.notify("draw_next")
        
        with open(f'python/messdaten/{filename}', mode='w', encoding='utf-8', newline='') as file:
            fieldnames = Werte_Liste[0].keys()    
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(Werte_Liste)
        Bridge.notify("hochzaehlenFinger")

def get_next_measurement_number():
    """Liest die letzte Messnummer aus der Datei und erhöht sie um 1"""
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
    """Loop wie der loop im Arduino Sketch. Hier wird eine LED rot blinken, um anzuzeigen, dass die MPU bereit ist und läuft"""
    # Blink LED 1 in red
    # Turn on the LED red segment(1, 0, 0)
    Leds.set_led1_color(1,0,0)
    time.sleep(1)   
    
    # Turn off the LED (0, 0, 0)
    Leds.set_led1_color(0,0,0)
    time.sleep(1)

# Start von dem Programm wie das normale Setup Skript
Bridge.provide("envlope_read", envlope_read) # bereitstellen von Python Funktionen für das MCU
Bridge.provide("messung_speichern",messung_speichern)
App.run(user_loop=loop) # Die LED soll im Loop laufen