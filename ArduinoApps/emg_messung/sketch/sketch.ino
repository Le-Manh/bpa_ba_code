#if defined(ARDUINO) && ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif

#include "EMGFilters.h"

// --- Konfiguration ---
// this build used 4 sensors
#define NUM_SENSORS 4
// 2000 µs -> 500 Hz other possibility: 1000µs -> 1000 Hz
#define SAMPLE_INTERVAL 2000

const uint16_t SAMPLE_INTERVAL_US = SAMPLE_INTERVAL;

// --- Sensor-Setup ---
int sensorPins[] = { A0, A1, A2, A3 };
EMGFilters myFilters[NUM_SENSORS];
float sensorOffsets[NUM_SENSORS];
#if SAMPLE_INTERVAL == 2000
SAMPLE_FREQUENCY sampleRate = SAMPLE_FREQ_500HZ;
#elif SAMPLE_INTERVAL == 1000
SAMPLE_FREQUENCY sampleRate = SAMPLE_FREQ_1000HZ;
#endif
NOTCH_FREQUENCY humFreq = NOTCH_FREQ_50HZ;  // This frequency is used to filter line voltages. If the line voltage use 60Hz it can be changed to: NOZCH_FREQ_60HZ

// --- Funktionsprototypen ---
void readAllSensors(uint32_t t_ms);
MsgPack::bin_t<uint8_t> get_emg_frame();
void hochzaehlenFinger();

void setup() {
  currentFinger = littleFinger;

  Serial.begin(115200);
  // Sensoren und Filter initialisieren
  for (int i = 0; i < NUM_SENSORS; i++) {
    pinMode(sensorPins[i], INPUT);
    myFilters[i].init(sampleRate, humFreq, true, true, true);
  }

  Serial.print("Wert\tAktuellerFinger\tSensor\n");
  calibrateSensors();
}

void loop() {
  unsigned long startMicros;
  startMicros = micros();
  readAllSensors();
  
}

void readAllSensors() {
  for (int i = 0; i < NUM_SENSORS; i++) {
    uint16_t rawValue = analogRead(sensorPins[i]);
    float filteredValue = myFilters[i].update(rawValue);
    Serial.print(filteredValue);
    Serial.print("\t");
    Serial.print((int)currentFinger);
    Serial.print("\t");
    Serial.print((int)sensorPins[i]);
    Serial.println();
  }
}

// --- Kalibrierung ---
void calibrateSensors() {
  const int calibrationSamples = 1000;
  long sums[NUM_SENSORS] = { 0 };

  for (int i = 0; i < calibrationSamples; i++) {
    unsigned long calibLoopStart = micros();
    for (int j = 0; j < NUM_SENSORS; j++) {
      sums[j] += myFilters[j].update(analogRead(sensorPins[j]));
    }
    unsigned long calibElapsedTime = micros() - calibLoopStart;
    if (calibElapsedTime < SAMPLE_INTERVAL_US) {                 // Ziel: sampleRate pro Sample
      delayMicroseconds(SAMPLE_INTERVAL_US - calibElapsedTime);  // um die Abtastrate konstant zu halten
    }
  }

  for (int i = 0; i < NUM_SENSORS; i++) {
    sensorOffsets[i] = (float)sums[i] / calibrationSamples;
  }
}

// CRC-16/IBM (Modbus) Beispiel: https://www.codegenes.net/blog/function-to-calculate-a-crc16-checksum/#what-is-crc16
uint16_t crc16_update(uint16_t crc, uint8_t data) {
  crc ^= data;                       // XOR mit crc und data
  for (uint8_t i = 0; i < 8; i++) {  // 8 mal weil data uint8_t ist
    if (crc & 1) {                   // AND mit CRC und 1 --> Kontrolle ob LSB eine 1 ist
      crc = (crc >> 1) ^ 0xA001;     // 0xA001 ist ein Polynom aus dem Algorithmus: https://codingtechroom.com/question/-implement-crc16-0xa001; Es wird eig ein 0x8005 genutzt. Mit 0xA001 ist ein bit reflektiert
    } else {
      crc >>= 1;  // Schieben wenn LSB 0 ist
    }
  }
  return crc;
}
