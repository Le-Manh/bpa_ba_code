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

// Visuell Feedback for finger
#include <Arduino_LED_Matrix.h>
#include "LED_Matrix.h"

// --- activate Timing Debug ---
// to activate Timing Debug change the value to 1 otherwise change it to 0
#define TIMING_DEBUG 0

// --- activate Data Debug ---
// This will print the value of DEBUG_SENSOR, this can be used to plot the data in Serial Plotter
// The endline would be new line
//to activate the Data Debug. Possible Values are 0 or 1
#define DATA_DEBUG 0
// possible Values are the Numeration of the sensor
#define DEBUG_SENSOR 0
//possible Values are rawValue or filteredValue, this will only work if DATA_DEBUG is 1
#define DEBUG_VALUE rawValue
// This can be used to write the rawValue into the Buffer
#define RAWDATA_INTO_BUFFER 0

// --- Konfiguration ---
// this build used 4 sensors
#define NUM_SENSORS 4
// 2000 µs -> 500 Hz other possibility: 1000µs -> 1000 Hz
#define SAMPLE_INTERVAL 2000 
// Ringgröße auf ein das nächsthöhere der Potenz von 2 gesetzt (geändert von 255 zu 512), bei RAWDATA_INTO_BUFFER == 1 sollte der Ring_Size auf 800 gesetzt werden. 512 führt zum Überlauf und 1024 ist zu viel
#define RING_SIZE 512
const uint16_t SAMPLE_INTERVAL_US = SAMPLE_INTERVAL; 

// --- Sensor-Setup ---
int sensorPins[] = {A0, A1, A2, A3};
EMGFilters myFilters[NUM_SENSORS];
float sensorOffsets[NUM_SENSORS];
#if SAMPLE_INTERVAL == 2000
SAMPLE_FREQUENCY sampleRate = SAMPLE_FREQ_500HZ;
#elif SAMPLE_INTERVAL == 1000
SAMPLE_FREQUENCY sampleRate = SAMPLE_FREQ_1000HZ;
#endif
NOTCH_FREQUENCY humFreq = NOTCH_FREQ_50HZ; // This frequency is used to filter line voltages. If the line voltage use 60Hz it can be changed to: NOZCH_FREQ_60HU

// --- Ringbuffer-Struktur ---
#define MAX_SAMPLES_PER_FRAME 128
struct Sample {
    float values[NUM_SENSORS]; // Array für die 4 Sensorwerte
    uint32_t t_ms;             // Zeitstempel in Millisekunden

    #if RAWDATA_INTO_BUFFER == 1
    uint16_t raw_values[NUM_SENSORS];
    #endif
};

Sample ringBuf[RING_SIZE];
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
void hochzaehlenFinger();

//interrupt und Feedback-LED
const byte ledPin = 12;
const byte interruptPin = 2;
volatile byte ledState = LOW;
volatile bool messungState = false;
volatile bool start_stop_mpu = false;
//Interrupt (ISR)
void button_interrupt_messung()
{
  ledState = !ledState;
  messungState = !messungState;
  start_stop_mpu = !start_stop_mpu;
}

// Interrupt Hand Wechsel
const byte fingerWechselPin = 6;
volatile bool rightHand = true;
// ISR
void button_interrupt_handswitch()
{
  rightHand = !rightHand;
}

// Timer-Callback wird bei jedem Intervall aufgerufen
static void onSampleTimer(struct k_timer *timer_id) {
    (void)timer_id;
    atomic_inc(&timer_ticks); // Sicher den Zähler erhöhen
}

#if TIMING_DEBUG == 1
  //--- Timing DEBUG Variablen ---
  volatile uint32_t processed_sample_count = 0;
  uint32_t last_report_time = 0;
#endif

// --- LED Matrix Feedback ---
Arduino_LED_Matrix matrix;
enum fingerState {littleFinger= 0, ringFinger,middleFinger,indexFinger,thumb};
int currentFinger;
uint8_t* matrix_feedback[] = {littleFinger_Frame, ringFinger_Frame, middleFinger_Frame, indexFinger_Frame, thumb_Frame};
bool changeFinger = false;

// define a function to expose this to the MPU
// So the MPU knows, if it has to decode more data
bool more_values_in_buffer(){
#if RAWDATA_INTO_BUFFER == 1
  return true;
#else
  return false;
#endif
}

void setup() {
    // start Matrix and feedback that MCU is running
    matrix.begin();
    matrix.setGrayscaleBits(1);
    matrix.draw(Hi_Frame); 
    currentFinger = littleFinger;

    // Bridge initialisieren und Funktion bereitstellen
    Bridge.begin(); //Bridge is communicating with baud 115200
    Bridge.provide("get_emg_frame", get_emg_frame);
    Bridge.provide("more_values_in_buffer", more_values_in_buffer);
  
    Monitor.begin(); //Monitor can only be 9600 baud
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

    // Zephyr Kernel Timer für 500 Hz starten
    k_timer_init(&sampleTimer, onSampleTimer, nullptr); // init und docs hier: https://docs.zephyrproject.org/latest/kernel/services/timing/timers.html#defining-a-timer
    k_timer_start(&sampleTimer, K_USEC(SAMPLE_INTERVAL_US), K_USEC(SAMPLE_INTERVAL_US)); //use of start timer: https://docs.zephyrproject.org/latest/kernel/services/timing/timers.html#using-a-timer-expiry-function

    //Feedback-LED Setup
    pinMode(ledPin, OUTPUT);

    //Interrupt-Setup
    pinMode(interruptPin,INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(interruptPin),button_interrupt_messung,FALLING); //attachInterrupt(pin, ISR, mode) 
    pinMode(fingerWechselPin, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(fingerWechselPin),button_interrupt_handswitch, FALLING);

    //Setup beendet:
    matrix.draw(matrix_feedback[currentFinger]);
}

void loop() {
    // Holen, wie viele Samples vom Timer getriggert wurden
    uint32_t pending_samples = atomic_set(&timer_ticks, 0);

    digitalWrite(ledPin,ledState);
    
    if (pending_samples == 0) {
        // Nichts zu tun, kurz schlafen, um CPU zu schonen
        k_sleep(K_USEC(200)); //200 microsseconds
    } else {
        // Alle anstehenden Samples verarbeiten
        while (pending_samples > 0) {
            sample_time_us += SAMPLE_INTERVAL_US;
            if (messungState) {
              unint32_t t_ms = k_uptime_get_32();
              readAllSensors(t_ms); // Zeit in ms übergeben
            }
            pending_samples--;
            #if TIMING_DEBUG == 1
              processed_sample_count++;  
            #endif
        }
      if (start_stop_mpu) {
        //Die Aufnahme der Messungen wird für jeden Finger einmal getriggert, um die Kommunikation zu verringern
        noInterrupts();
        Bridge.notify("start_stop", rightHand);
        start_stop_mpu = !start_stop_mpu;
        interrupts();
        // changes Finger and Matrix only on the 2nd push of the interrupt
        if (changeFinger) {
          hochzaehlenFinger();
          matrix.draw(matrix_feedback[currentFinger]);
          }
        changeFinger = !changeFinger;
        }
      }
    
      #if TIMING_DEBUG == 1   
      // Einmal pro Sekunde einen Bericht ausgeben nur im DEBUG wichtig
      uint32_t current_time = millis();
      if (current_time - last_report_time >= 1000) {
          Monitor.print("Sample Rate: ");
          Monitor.print(processed_sample_count);
          Monitor.println(" Hz");
        
          processed_sample_count = 0;
          last_report_time = current_time;
      }
      #endif
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
        unint16_t rawValue = analogRead(sensorPins[i]);
        float filteredValue = myFilters[i].update(rawValue);
        
        // Debug wenn die Daten in den Serial Monitor/Plotter ausgegeben werden soll
        #if DATA_DEBUG == 1
        //Auslesen des Sensor und Normierung auf 3V bei einem 14 Bit ADC. Da Arduino Uno Q floats nicht richtig ausgibt, wird es auf 10000 normiert. 10000 entspricht also ein 1V
        if(i == DEBUG_SENSOR) {
          int16_t voltageValue = DEBUG_VALUE * (3/(pow(2.0,14.0))) * 10000;
          Monitor.println(voltageValue);
        }
        #endif

        ringBuf[head].values[i] = filteredValue - sensorOffsets[i];
        #if RAWDATA_INTO_BUFFER == 1
        ringBuf[head].raw_values[i] = rawValue;
        #endif
    }
    head = next;
}

MsgPack::bin_t<uint8_t> get_emg_frame() {
    // --- Kritischer Abschnitt START ---
    noInterrupts();
    // Variablen vom Ringbuffer auslesen und als kopie überführen
    uint16_t tail = last_sent;
    uint16_t h = head;
    bool ovf = overflowed;
    overflowed = false;
    interrupts();
    // --- Kritischer Abschnitt ENDE ---

    MsgPack::bin_t<uint8_t> out; // Ergebnis als MsgPack verpacken und dann versenden über die Bridge, bin_t ist ein Alias für std::vector aus msgPack: https://msgpack.org/#type-aliases-for-str--bin--array--map
    uint16_t count = (h >= tail) ? (h - tail) : (RING_SIZE - tail + h); // Abzählen wie viele Werte im Buffer sind, da es ein Ringbuffer ist kann tail auch größer sein als head. Deswegen der tertiäre Operator
    
    if (count == 0) return out; // Keine Werte vorhanden

    #if RAWDATA_INTO_BUFFER == 1
    static uint8_t frame[2 + 4 + RING_SIZE * (1 + sizeof(float) * sizeof(int) * NUM_SENSORS) + 2];
    #else
    // frame wird als Buffer genutzt, worst case Größe eines Frames:
    static uint8_t frame[2 + 4 + RING_SIZE * (1 + sizeof(float) * NUM_SENSORS) + 2]; 
    /* Die magic Numbers setzen sich zusammen aus:
      2: variable count (uint16_t) --> 2 Byte
      4: variable t0/Zeitstempel (uint_32t) --> 4 Byte
      RING_SIZE * (1 + sizeof(float) * NUM_SENSORS) Maximale Größe aller Daten im Puffer, die Magic Number hier ist die Göße eines Bytes ; floats sind auf dem Arduino 4 Byte groß
      2: Größe der CRC Prüfsumme (uint16_t) -–> 2 Byte
    */
    #endif
    size_t idx = 0;
    uint16_t crc = 0;

    uint16_t frame_count = min<uint16_t>(count,MAX_SAMPLES_PER_FRAME); // Erhöhung des frames von 8-Bit auf 16 um den höheren Buffer abzufangen
    memcpy(&frame[idx], &frame_count, sizeof(frame_count));
	idx += sizeof(frame_count);

    // Zeitstempel des ersten Samples lesen (ist sicher, da h nicht über tail hinausläuft)
    uint32_t t0 = ringBuf[tail].t_ms; // den zuletzt gesendeten Zeitstempel auslesen
  
    // memcpy (memorycopy) void* memcpy( void* dest, const void* src, std::size_t count ); aus https://en.cppreference.com/cpp/string/byte/memcpy
    memcpy(&frame[idx], &t0, sizeof(t0)); // kopiert den Zeitstempel ins frame, die Anzahl an kopierten Bits wird von sizeof(t0) bestimmt
  
    idx += sizeof(t0); // Array wird weitergeschoben um die Größe des Zeitstempels

    uint32_t prev_t = t0; // speichern des letzten gelesenen Zeitstempels
    uint16_t current_read_idx = tail; // den derzeitigen auszulesenen Puffer Teil aufnehmen
    for (uint16_t i = 0; i < frame_count; i++) { // läuft so lange wie die anzahl an Daten die wir aus dem Puffer lesen sollten
        // Erstelle eine lokale, nicht-volatile Kopie des Datensatzes
        // durch eine explizite Speicher-Kopie.
        Sample local_sample;
        memcpy(&local_sample, (const void*)&ringBuf[current_read_idx], sizeof(Sample)); // kopiert den ringBuf in die neu erstellte Variable
        
        uint32_t dt = local_sample.t_ms - prev_t; // wir speichern nur das delta um die Menge an Daten zu reduzieren
        frame[idx++] = (dt > 255) ? 255 : (uint8_t)dt; // Falls dt zu groß wird müssen wir es auf 8 Bit reduzieren
        prev_t = local_sample.t_ms; // speichern des letzten t_ms um die Daten danach auch richtig aufzunehmen
        
        // Jetzt mit der sicheren, lokalen Kopie arbeiten
        memcpy(&frame[idx], local_sample.values, sizeof(float) * NUM_SENSORS); // Kopieren der Werte in den Frame
        idx += sizeof(float) * NUM_SENSORS; // Verschieben des Index um die Größe der Messwerte

        #if RAWDATA_INTO_BUFFER == 1
        memcpy(&frame[idx], local_sample.raw_values, sizeof(int)*NUM_SENSORS);
        idx += sizeof(int) * NUM_SENSORS;
        #endif

        current_read_idx = (current_read_idx + 1) % RING_SIZE;
    }

    // CRC16 berechnen (cyclic redundancy check)
    for (size_t i = 0; i < idx; i++) {
        crc = crc16_update(crc, frame[i]); // crc für jeden index im Frame berechnen
    }
    memcpy(&frame[idx], &crc, sizeof(crc)); // kopieren des berechneten crc in das frame
    idx += sizeof(crc); // Erhöhung des Index um die größe des crc

    // Lesezeiger (last_sent) atomar aktualisieren
    noInterrupts();
    last_sent = current_read_idx; // aktualisierung des last_sent
    interrupts();
    
    if (ovf) {
        out.push_back(0x21); // 0x21 ASCII Zeichen für '!' wird ans Ende angehangen wenn ein Overflow im RingBuffer passiert ist https://en.cppreference.com/cpp/container/vector/push_back
    }

    // Frame in den MsgPack-Container kopieren
    out.insert(out.end(),frame, frame + idx); // vector out wird der frame inserted: https://en.cppreference.com/cpp/container/vector/insert, hier wird ausgenutzt, dass Pointer iterables sind

    return out;
}

// --- Kalibrierung ---
void calibrateSensors() {
    const int calibrationSamples = 2000;
    long sums[NUM_SENSORS] = {0};

    for (int i = 0; i < calibrationSamples; i++) {
         unsigned long calibLoopStart = micros();
        for (int j = 0; j < NUM_SENSORS; j++) {
            sums[j] += myFilters[j].update(analogRead(sensorPins[j]));
        }
        unsigned long calibElapsedTime = micros() - calibLoopStart;
        if(calibElapsedTime < SAMPLE_INTERVAL_US) { // Ziel: sampleRate pro Sample
          delayMicroseconds(SAMPLE_INTERVAL_US - calibElapsedTime); // um die Abtastrate konstant zu halten
        }
    }

    for (int i = 0; i < NUM_SENSORS; i++) {
        sensorOffsets[i] = (float)sums[i] / calibrationSamples;
    }
}

// CRC-16/IBM (Modbus) Beispiel: https://www.codegenes.net/blog/function-to-calculate-a-crc16-checksum/#what-is-crc16
uint16_t crc16_update(uint16_t crc, uint8_t data) {
    crc ^= data; // XOR mit crc und data
    for (uint8_t i = 0; i < 8; i++) { // 8 mal weil data uint8_t ist
        if (crc & 1) { // AND mit CRC und 1 --> Kontrolle ob LSB eine 1 ist
            crc = (crc >> 1) ^ 0xA001; // 0xA001 ist ein Polynom aus dem Algorithmus: https://codingtechroom.com/question/-implement-crc16-0xa001; Es wird eig ein 0x8005 genutzt. Mit 0xA001 ist ein bit reflektiert
        } else {
            crc >>= 1; // Schieben wenn LSB 0 ist
        }
    }
    return crc;
}

// Hilfsfunktion zum Beschreiben der LED Matrix
void hochzaehlenFinger()
{
  if(currentFinger != thumb)
  {
    currentFinger ++; // ist der currentFinger != Daumen --> wird hochgezaehlt
  }else{ 
    currentFinger = littleFinger;     // anderenfalls wird currentFinger = kleiner Finger gesetzt
  }
}
