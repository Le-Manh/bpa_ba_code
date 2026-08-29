import csv
import struct
import os
import pandas as pd
from arduino.app_utils import App, Bridge, Leds

DATA_DEBUG = False # used to rename output data to debug.csv instead of messung_[rl]_[0-9]+.csv

SAMPLE_FORMAT = '<Bffff'
SAMPLE_SIZE = struct.calcsize(SAMPLE_FORMAT)

def crc16_update(crc, data):
    crc ^= data
    for _ in range(8):
        crc = (crc >> 1) ^ 0xA001 if (crc & 1) else (crc >> 1)
    return crc


def parse_emg_frame(payload: bytes) -> list[tuple[float, float, float, float, float]] | None:

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
    samples = []
    for i in range(count):
        dt_ms, v1, v2, v3, v4 = struct.unpack_from(SAMPLE_FORMAT, payload, offset)

        if i > 0:
            current_time_ms += dt_ms

        samples.append((current_time_ms, v1, v2, v3, v4))
        offset += SAMPLE_SIZE

    return samples