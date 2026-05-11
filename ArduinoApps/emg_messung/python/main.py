import time
from arduino.app_utils import App, Bridge, Leds
import csv
import string

# globale Variablen, die im gesamten Skripe gleichbleiben
Werte_Liste = list()
sensoren_index = range(5)
fingerState = range(6)
messungState = False

def func_messungState(messungState_arduino):
    global messungState
    messungState = messungState_arduino

def messung_speichern():
    """Speichert die Messung aus Werte_Liste in eine csv und nummeriert die Messung basierend auf der last_measurement.txt
        Da diese Funktion auch immer von der MCU Seite aufgerufen wird, wird die Variable werteVorhanden übergegeben, um sicherzustellen, dass Werte_Liste auch vollständig ist und gerade nicht beschrieben wird
    """
    print("es wird gespeichert")
    global filename # Das wird gebraucht, damit beim nächsten Aufruf die Funktion noch weiß, wie die Datei hieß
    global Werte_Liste
    '''
    measurement_number = get_next_measurement_number()
    filename = f"Messung_{measurement_number}.csv"
    with open("python/messdaten/last_measurement.txt", "w") as f:
        f.write(str(measurement_number))
    '''    
    with open(f'python/messdaten/debug.csv', mode='w', encoding='utf-8', newline='') as file:
        fieldnames = Werte_Liste[0].keys()    
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(Werte_Liste)
    Werte_Liste.clear()
            

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
    """Loop wie der loop im Arduino Sketch"""
    if(messungState):
        startTime = time.time()
            wert = Bridge.call("messung_sensoren",finger,sensor)
        
            #Werte_Liste.append({"Aktueller Finger" : finger, "sensoren": sensor, "Wert":wert})
        endTime = time.time()
        elapsedTime = endTime-startTime 
        print(elapsedTime)
        time.sleep(elapsedTime)
    #print(Werte_Liste)

# Start von dem Programm wie das normale Setup Skript
Bridge.provide("messung_speichern",messung_speichern)
Bridge.provide("messungState",func_messungState)
App.run(user_loop=loop) # Die LED soll im Loop laufen