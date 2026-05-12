import time
import struct
import csv
from arduino.app_utils import App, Bridge, Leds

# Globale Liste zum Sammeln aller Messdaten
all_measurements = []
is_recording = False
current_finger_state = 0 # 0=little, 1=ring, etc.

# Paylod-Format:
# <B: count
# <I: t0_ms
# [ <B: dt_ms, <f: val1, <f: val2, <f: val3, <f: val4 ] x count
# <H: crc16
# Das '<' bedeutet Little-Endian Byte Order.
SAMPLE_FORMAT = '<Bffff' # Format für ein Sample: dt_ms und 4 floats
SAMPLE_SIZE = struct.calcsize(SAMPLE_FORMAT)

def crc16_update(crc, data):
    """CRC-16/IBM (Modbus) Berechnung in Python."""
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
    if payload and payload[0] == 0x21: # '!'
        print("WARNUNG: MCU-Puffer ist übergelaufen! Einige Samples gingen verloren.")
        payload = payload[1:]

    if len(payload) < 7: # Mindestgröße: count(1) + t0(4) + crc(2)
        return

    # CRC-Prüfsumme verifizieren
    crc_from_mcu = struct.unpack('<H', payload[-2:])[0]
    calculated_crc = 0
    for byte in payload[:-2]:
        calculated_crc = crc16_update(calculated_crc, byte)

    if crc_from_mcu != calculated_crc:
        print(f"FEHLER: CRC-Prüfsumme stimmt nicht überein! MCU: {crc_from_mcu}, Kalkuliert: {calculated_crc}. Verwerfe Paket.")
        return

    # Daten entpacken
    try:
        count, t0_ms = struct.unpack_from('<BI', payload, 0)
        offset = 5 # Start nach count und t0
        
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
    """Wird per Bridge-Button oder einer anderen Logik getriggert."""
    global is_recording, all_measurements
    is_recording = not is_recording
    
    if is_recording:
        print("Aufnahme gestartet...")
        all_measurements = [] # Alte Daten löschen
        Leds.set_led1_color(0, 1, 0) # Grüne LED für Aufnahme
    else:
        print("Aufnahme gestoppt. Speichere Daten...")
        Leds.set_led1_color(1, 0, 0) # Rote LED für Stopp
        save_data()
        Leds.set_led1_color(0, 0, 0) # LED aus

def save_data():
    """Speichert die gesammelten Daten in einer CSV-Datei."""
    if not all_measurements:
        print("Keine Daten zum Speichern vorhanden.")
        return

    # Dateiname z.B. messung_finger0_1678886400.csv
    filename = f"messdaten/messung_finger{current_finger_state}_{int(time.time())}.csv"
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = all_measurements[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_measurements)
        print(f"Daten erfolgreich in '{filename}' gespeichert.")
    except Exception as e:
        print(f"Fehler beim Speichern der Datei: {e}")

def user_loop():
    """Hauptschleife auf der MPU-Seite."""
    if is_recording:
        try:
            # Datenblock von der MCU abholen
            frame = Bridge.call("get_emg_frame")
            if frame:
                parse_emg_frame(bytes(frame))
        except Exception as e:
            print(f"Fehler bei Bridge.call: {e}")

    time.sleep(0.1) # Alle 100ms nach neuen Daten fragen

# --- Setup ---
if __name__ == "__main__":
    # Diese Funktionen könnten z.B. an die Buttons des Arduino Portenta gebunden werden
    Bridge.provide("start_stop", start_stop_recording)
    App.run(user_loop=user_loop)