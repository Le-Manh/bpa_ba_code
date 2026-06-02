import csv
import time
import struct
import os
from arduino.app_utils import App, Bridge, Leds

DATA_DEBUG = False # used to rename output data to debug.csv instead of messung_[rl]_[0-9]+.csv
TIMING_DEBUG = False # used to measure the time to get one frame

is_recording = False
csvfile = None
writer = None
measurement_number = -1 #if it's -1 sth is wrong

dict_finger = {"littleFinger": 0, "ringFinger": 1, "middleFinger": 2, "indexFinger": 3, "thumb": 4}
current_finger_state = dict_finger["littleFinger"]
handState = True

RAW_DATA_IN_BUFFER = Bridge.call("more_values_in_buffer")

if RAW_DATA_IN_BUFFER:
    SAMPLE_FORMAT = '<BffffHHHH'   # dt + 4 floats + 4x uint16 raw
else:
    SAMPLE_FORMAT = '<Bffff'
SAMPLE_SIZE = struct.calcsize(SAMPLE_FORMAT)

def crc16_update(crc, data):
    crc ^= data
    for _ in range(8):
        crc = (crc >> 1) ^ 0xA001 if (crc & 1) else (crc >> 1)
    return crc


def get_next_available_filename(hand: str):
    n = get_next_measurement_number()
    while True:
        filename = f"python/messdaten/messung_{hand}_{n}.csv"
        if not os.path.exists(filename):
            return filename, n
        n += 1

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

def open_new_csv():
    global csvfile, writer, measurement_number
    hand = "r" if handState else "l"
    if DATA_DEBUG:
        filename = f"python/messdaten/debug_{hand}.csv"
        measurement_number = 0 #to prevent compatibility issues
    else:
        filename, measurement_number = get_next_available_filename(hand)

    csvfile = open(filename, 'w', newline='', encoding='utf-8')
    if RAW_DATA_IN_BUFFER:
        fieldnames = ["Aktueller Finger","timestamp_ms","sensor_0","sensor_1","sensor_2","sensor_3",
                      "raw_sensor_0","raw_sensor_1","raw_sensor_2","raw_sensor_3"]
    else:
        fieldnames = ["Aktueller Finger","timestamp_ms","sensor_0","sensor_1","sensor_2","sensor_3"]

    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    csvfile.flush()
    print(f"Schreibe live nach {filename}")

def close_csv():
    global csvfile, writer, measurement_number
    if csvfile:
        csvfile.flush()
        csvfile.close()

        if not DATA_DEBUG:
            with open("python/messdaten/last_measurement.txt", "w") as f:
                f.write(str(measurement_number))

    csvfile = None
    writer = None

def parse_emg_frame(payload: bytes):
    global writer

    if not payload or len(payload) < 8:
        return

    # overflow marker optional
    if payload[0] == 0x21:
        print("WARN: overflow on MCU")
        payload = payload[1:]

    crc_from_mcu = struct.unpack('<H', payload[-2:])[0]
    crc_calc = 0
    for b in payload[:-2]:
        crc_calc = crc16_update(crc_calc, b)
    if crc_from_mcu != crc_calc:
        print("CRC error, drop frame")
        return

    count, t0_ms = struct.unpack_from('<HI', payload, 0)
    offset = 6
    current_time_ms = t0_ms

    # optional: Plausibilitätscheck Länge
    expected_len = 6 + count * SAMPLE_SIZE + 2
    if expected_len != len(payload):
        # nicht zwingend fatal, aber hilfreich beim Debuggen
        # print(f"Len mismatch exp={expected_len} got={len(payload)}")
        pass

    for i in range(count):
        if RAW_DATA_IN_BUFFER:
            dt_ms, v1, v2, v3, v4, rv1, rv2, rv3, rv4 = struct.unpack_from(SAMPLE_FORMAT, payload, offset)
        else:
            dt_ms, v1, v2, v3, v4 = struct.unpack_from(SAMPLE_FORMAT, payload, offset)

        if i > 0:
            current_time_ms += dt_ms

        row = {
            "Aktueller Finger": current_finger_state,
            "timestamp_ms": current_time_ms,
            "sensor_0": v1, "sensor_1": v2, "sensor_2": v3, "sensor_3": v4
        }
        if RAW_DATA_IN_BUFFER:
            row.update({
                "raw_sensor_0": rv1, "raw_sensor_1": rv2,
                "raw_sensor_2": rv3, "raw_sensor_3": rv4
            })

        if writer:
            writer.writerow(row)

        offset += SAMPLE_SIZE

    # für Live-Betrieb regelmäßig flushen (Tradeoff IO vs Sicherheit)
    if csvfile:
        csvfile.flush()

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
                parse_emg_frame(bytes(frame))
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