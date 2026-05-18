#if defined(ARDUINO) && ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif

#include "EMGFilters.h"
#include "Arduino_RouterBridge.h"
#include <MsgPack.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/atomic.h>

// --- Konfiguration ---
#define NUM_SENSORS 4
const uint16_t SAMPLE_INTERVAL_US = 1000; // 1000 µs -> 1000 Hz
const uint16_t RING_SIZE = 256;          // Puffer für 256 Samples (~256 ms bei 1kHz)

// --- Sensor-Setup ---
int sensorPins[] = {A0, A1, A2, A3};
EMGFilters myFilters[NUM_SENSORS];
float sensorOffsets[NUM_SENSORS];
SAMPLE_FREQUENCY sampleRate = SAMPLE_FREQ_500HZ;
NOTCH_FREQUENCY humFreq = NOTCH_FREQ_50HZ;

// --- Ringbuffer-Struktur ---
struct Sample {
    float values[NUM_SENSORS]; // Array für die 4 Sensorwerte
    uint32_t t_ms;             // Zeitstempel in Millisekunden
};

volatile Sample ringBuf[RING_SIZE];
volatile uint16_t head = 0;       // Nächste Schreibposition
volatile uint16_t last_sent = 0;  // Position nach dem letzten gesendeten Sample
volatile bool overflowed = false; // Flag für Pufferüberlauf

// --- Timer für präzise Abtastung (via Zephyr Kernel) ---
static struct k_timer sampleTimer;
atomic_t timer_ticks = ATOMIC_INIT(0); // Atomarer Zähler für anstehende Samples
uint32_t sample_time_us = 0;

// --- Funktionsprototypen ---
void readAllSensors(uint32_t t_ms);
MsgPack::bin_t<uint8_t> get_emg_frame();
void calibrateSensors();
uint16_t crc16_update(uint16_t crc, uint8_t data);

//interrupt und Feedback-LED
const byte ledPin = 12;
const byte interruptPin = 2;
volatile byte ledState = LOW;
volatile bool messungState = false;
//Interrupt (ISR)
void button_interrupt()
{
  ledState = !ledState;
  messungState = !messungState;
}

// Timer-Callback wird bei jedem Intervall aufgerufen
static void onSampleTimer(struct k_timer *timer_id) {
    (void)timer_id;
    atomic_inc(&timer_ticks); // Sicher den Zähler erhöhen
}

void setup() {
    Monitor.begin(115200);
    Monitor.println("HAWK EMG-System startet...");

    // Sensoren und Filter initialisieren
    for (int i = 0; i < NUM_SENSORS; i++) {
        pinMode(sensorPins[i], INPUT);
        myFilters[i].init(sampleRate, humFreq, true, true, true);
    }
    
    // Kurze Verzögerung, um der MPU Zeit zum Starten zu geben
    delay(1000); 
    Monitor.println("Kalibrierung startet...");
    calibrateSensors();
    Monitor.println("Kalibrierung abgeschlossen.");

    // Bridge initialisieren und Funktion bereitstellen
    Bridge.begin();
    Bridge.provide("get_emg_frame", get_emg_frame);

    // Zephyr Kernel Timer für 1000 Hz starten
    k_timer_init(&sampleTimer, onSampleTimer, nullptr);
    k_timer_start(&sampleTimer, K_USEC(SAMPLE_INTERVAL_US), K_USEC(SAMPLE_INTERVAL_US));

    //Feedback-LED Setup
    pinMode(ledPin, OUTPUT);

    //Interrupt-Setup
    pinMode(interruptPin,INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(interruptPin),button_interrupt,FALLING); //attachInterrupt(pin, ISR, mode) 
}

void loop() {
    // Holen, wie viele Samples vom Timer getriggert wurden
    uint32_t pending_samples = atomic_set(&timer_ticks, 0);
    if (messungState){
      Bridge.notify("start_stop");
      messungState = !messungState;
    }

    digitalWrite(ledPin,ledState);
    
    if (pending_samples == 0) {
        // Nichts zu tun, kurz schlafen, um CPU zu schonen
        k_sleep(K_USEC(200)); //200 micros?
    } else {
        // Alle anstehenden Samples verarbeiten
        while (pending_samples > 0) {
            sample_time_us += SAMPLE_INTERVAL_US;
            readAllSensors(sample_time_us / 1000); // Zeit in ms übergeben
            pending_samples--;
        }
    }
    // Die Bridge-Kommunikation läuft im Hintergrund und blockiert den Loop nicht.
}

void readAllSensors(uint32_t t_ms) {
    uint16_t next = (head + 1) % RING_SIZE;

    // Pufferüberlauf prüfen: Wenn der nächste Schreib-Index den Lese-Index einholt
    if (next == last_sent) {
        overflowed = true;
        // Ältestes Element verwerfen, indem der Lese-Zeiger verschoben wird
        last_sent = (last_sent + 1) % RING_SIZE;
    }

    ringBuf[head].t_ms = t_ms;
    for (int i = 0; i < NUM_SENSORS; i++) {
        int rawValue = analogRead(sensorPins[i]);
        float filteredValue = myFilters[i].update(rawValue);
        ringBuf[head].values[i] = filteredValue - sensorOffsets[i];
    }
    
    head = next;
}

MsgPack::bin_t<uint8_t> get_emg_frame() {
    // --- Kritischer Abschnitt START ---
    noInterrupts();
    uint16_t tail = last_sent;
    uint16_t h = head;
    bool ovf = overflowed;
    overflowed = false;
    interrupts();
    // --- Kritischer Abschnitt ENDE ---

    MsgPack::bin_t<uint8_t> out;
    uint16_t count = (h >= tail) ? (h - tail) : (RING_SIZE - tail + h);
    
    if (count == 0) return out;

    static uint8_t frame[1 + 4 + RING_SIZE * (1 + sizeof(float) * NUM_SENSORS) + 2];
    size_t idx = 0;
    uint16_t crc = 0;

    uint8_t frame_count = (count > 255) ? 255 : count;
    frame[idx++] = frame_count;

    // Zeitstempel des ersten Samples lesen (ist sicher, da h nicht über tail hinausläuft)
    uint32_t t0 = ringBuf[tail].t_ms;
    memcpy(&frame[idx], &t0, sizeof(t0));
    idx += sizeof(t0);

    uint32_t prev_t = t0;
    uint16_t current_read_idx = tail;
    for (uint16_t i = 0; i < frame_count; i++) {
        // === KORREKTUR START ===
        // Erstelle eine lokale, nicht-volatile Kopie des Datensatzes
        // durch eine explizite Speicher-Kopie.
        Sample local_sample;
        memcpy(&local_sample, (const void*)&ringBuf[current_read_idx], sizeof(Sample));
        // === KORREKTUR ENDE ===
        
        uint32_t dt = local_sample.t_ms - prev_t;
        frame[idx++] = (dt > 255) ? 255 : (uint8_t)dt;
        prev_t = local_sample.t_ms;
        
        // Jetzt mit der sicheren, lokalen Kopie arbeiten - das funktioniert.
        memcpy(&frame[idx], local_sample.values, sizeof(float) * NUM_SENSORS);
        idx += sizeof(float) * NUM_SENSORS;
        
        current_read_idx = (current_read_idx + 1) % RING_SIZE;
    }

    // CRC16 berechnen
    for (size_t i = 0; i < idx; i++) {
        crc = crc16_update(crc, frame[i]);
    }
    memcpy(&frame[idx], &crc, sizeof(crc));
    idx += sizeof(crc);

    // Lesezeiger (last_sent) atomar aktualisieren
    noInterrupts();
    last_sent = current_read_idx;
    interrupts();
    
    if (ovf) {
        out.push_back(0x21); // '!'
    }

    // Frame in den MsgPack-Container kopieren
    out.assign(frame, frame + idx); 

    return out;
}

// --- Hilfsfunktionen (Kalibrierung & CRC) ---
void calibrateSensors() {
    const int calibrationSamples = 2000;
    long sums[NUM_SENSORS] = {0};

    for (int i = 0; i < calibrationSamples; i++) {
        for (int j = 0; j < NUM_SENSORS; j++) {
            sums[j] += myFilters[j].update(analogRead(sensorPins[j]));
        }
        delayMicroseconds(SAMPLE_INTERVAL_US);
    }

    for (int i = 0; i < NUM_SENSORS; i++) {
        sensorOffsets[i] = (float)sums[i] / calibrationSamples;
        Monitor.print("Sensor "); Monitor.print(i);
        Monitor.print(" Offset: "); Monitor.println(sensorOffsets[i]);
    }
}

// CRC-16/IBM (Modbus)
uint16_t crc16_update(uint16_t crc, uint8_t data) {
    crc ^= data;
    for (uint8_t i = 0; i < 8; i++) {
        if (crc & 1) {
            crc = (crc >> 1) ^ 0xA001;
        } else {
            crc >>= 1;
        }
    }
    return crc;
}