import time
import struct # dieses Modul kann C structs zu Python objekte konvertieren
import csv
from arduino.app_utils import App, Bridge, Leds

TIMING_DEBUG = False # used to measure the time to get one frame

# Globale Liste zum Sammeln aller Messdaten
all_measurements = []
is_recording = False
dict_finger = {"littleFinger": 0, "ringFinger": 1, "middleFinger": 2, "indexFinger": 3, "thumb": 4}
current_finger_state = dict_finger["littleFinger"]

# Payload-Format: to get payload characters: https://docs.python.org/3/library/struct.html#format-characters
# <B: count (B: unsigned char (uint8_t)) --> int (Python)
# <I: t0_ms (I: unsigned int (uint32_t)) --> int (Python)
# [ <B: dt_ms, <f: val1, <f: val2, <f: val3, <f: val4 ] x count (f steht für float (4 Byte)) --> float (python)
# <H: crc16 (H: unsigned short (uint16_t)) --> int (Python)
# Das '<' bedeutet Little-Endian Byte Order.
SAMPLE_FORMAT = '<Bffff' # Format für ein Sample: dt_ms und 4 floats
SAMPLE_SIZE = struct.calcsize(SAMPLE_FORMAT)

def crc16_update(crc, data):
    """CRC-16/IBM (Modbus) Berechnung in Python. Die Berechnung ist genauso wie auf der MCU Seite"""
    crc ^= data
    for _ in range(8):
        if crc & 1:
            crc = (crc >> 1) ^ 0xA001
        else:
            crc >>= 1
    return crc

def parse_emg_frame(payload: bytes):
    """
    Deserialisiert das binäre Datenpaket von der MCU.
    """
    global all_measurements
    
    # Prüfen, ob ein Overflow-Flag gesendet wurde
    if payload and payload[0] == 0x21: # 0x21 ASCII: '!', im Payload steht an erster Stelle das '!', wenn es zu einem ovf kam
        print("WARNUNG: MCU-Puffer ist übergelaufen! Einige Samples gingen verloren.")
        payload = payload[1:]

    if len(payload) < 8: # Mindestgröße: count(2) + t0(4) + crc(2)
        return

    # CRC-Prüfsumme verifizieren
    crc_from_mcu = struct.unpack('<H', payload[-2:])[0] # Einlesen des crc Dabei nur die letzten beiden Bytes, wo unser CRC abegelegt worden ist, Das [0] ist wichtig, weil die Rückgabe von struct.unpack immer ein tuple ist also: '(crc,)'
    calculated_crc = 0
    for byte in payload[:-2]:
        calculated_crc = crc16_update(calculated_crc, byte) # eigene Berechnung auf MPU Seite

    if crc_from_mcu != calculated_crc:
        print(f"FEHLER: CRC-Prüfsumme stimmt nicht überein! MCU: {crc_from_mcu}, Kalkuliert: {calculated_crc}. Verwerfe Paket.")
        return

    # Daten entpacken
    try:
        count, t0_ms = struct.unpack_from('<HI', payload, 0)
        offset = 6 # Start nach count und t0, weil count 2 Byte (uint16_t) groß ist und t0 4 Byte (uint32_t)) --> 6 byte
        
        current_time_ms = t0_ms
        
        for i in range(count):
            dt_ms, v1, v2, v3, v4 = struct.unpack_from(SAMPLE_FORMAT, payload, offset)
            if i > 0:
                current_time_ms += dt_ms
            
            all_measurements.append({
                "finger": current_finger_state,
                "timestamp_ms": current_time_ms,
                "sensor_0": v1,
                "sensor_1": v2,
                "sensor_2": v3,
                "sensor_3": v4
            })
            offset += SAMPLE_SIZE

    except struct.error as e:
        print(f"Fehler beim Entpacken der Daten: {e}")


def start_stop_recording():
    """Wird per Interrupt im MCU getriggert"""
    global is_recording, all_measurements, current_finger_state
    is_recording = not is_recording
    if is_recording:
        if current_finger_state == dict_finger["littleFinger"]:
                print("Aufnahme gestartet...")
                all_measurements = [] # Alte Daten löschen
        Leds.set_led1_color(0, 1, 0) # Grüne LED für Aufnahme      
    else:
        if current_finger_state == dict_finger["thumb"]:
                print("Aufnahme gestoppt. Speichere Daten...")
                Leds.set_led1_color(1, 0, 0) # Rote LED für Stopp
                save_data()
                Leds.set_led1_color(0, 0, 0) # LED aus
                current_finger_state = dict_finger["littleFinger"]
        else:
            current_finger_state += 1 # wir gehen immer von kleinsten zum größten Finger
            print(f"der derzeitige Finger ist: Finger {current_finger_state}")

def save_data():
    """Speichert die gesammelten Daten in einer CSV-Datei."""
    if not all_measurements:
        print("Keine Daten zum Speichern vorhanden.")
        return

    measurement_number = get_next_measurement_number()
    # Dateiname z.B. messung_1.csv
    filename = f"python/messdaten/messung_{measurement_number}.csv"
    with open("python/messdaten/last_measurement.txt", "w") as f:
        f.write(str(measurement_number))
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = all_measurements[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_measurements)
        print(f"Daten erfolgreich in '{filename}' gespeichert.")
    except Exception as e:
        print(f"Fehler beim Speichern der Datei: {e}")

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


def user_loop():
    """Hauptschleife auf der MPU-Seite."""
    if is_recording:
        try:
            # Datenblock von der MCU abholen
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
                parse_emg_frame(bytes(frame))
                if TIMING_DEBUG:
                    end = time.time()
                    dt_parsing_emg_frame = end - start
                    print(f"Parsing Frame needed: {dt_parsing_emg_frame} s")
                    print(f"Time of both: {dt_get_emg_frame + dt_parsing_emg_frame}")
        except Exception as e:
            print(f"Fehler bei Bridge.call: {e}")
    
    time.sleep(0.01) # Alle 10ms nach neuen Daten fragen

# --- Setup ---
if __name__ == "__main__":
    # Diese Funktionen könnten z.B. an die Buttons des Arduino Portenta gebunden werden
    Bridge.provide("start_stop", start_stop_recording)
    App.run(user_loop=user_loop)