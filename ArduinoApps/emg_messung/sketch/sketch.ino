/*
* Copyright 2017, OYMotion Inc.
* All rights reserved.
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions
* are met:
*
* 1. Redistributions of source code must retain the above copyright
*    notice, this list of conditions and the following disclaimer.
*
* 2. Redistributions in binary form must reproduce the above copyright
*    notice, this list of conditions and the following disclaimer in
*    the documentation and/or other materials provided with the
*    distribution.
*
* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
* "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
* LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
* FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
* COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
* INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
* BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
* OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
* AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
* OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
* THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
* DAMAGE.
*
*/

#if defined(ARDUINO) && ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif

#include "EMGFilters.h"

#define SensorInputPin A0 // input pin number
#define SensorInputPin1 A1 // input pin number
#define SensorInputPin2 A2 // input pin number
#define SensorInputPin3 A3 // input pin number

#define debug 1

#include "Arduino_RouterBridge.h"

//Visuell feedback for finger
#include <Arduino_LED_Matrix.h>
#include "LED_Matrix.h"

// discrete filters must works with fixed sample frequence
// our emg filter only support "SAMPLE_FREQ_500HZ" or "SAMPLE_FREQ_1000HZ"
// other sampleRate inputs will bypass all the EMG_FILTER
SAMPLE_FREQUENCY sampleRate = SAMPLE_FREQ_500HZ;
// For countries where power transmission is at 50 Hz
// For countries where power transmission is at 60 Hz, need to change to
// "NOTCH_FREQ_60HZ"
// our emg filter only support 50Hz and 60Hz input
// other inputs will bypass all the EMG_FILTER
NOTCH_FREQUENCY humFreq = NOTCH_FREQ_50HZ;

//Aus der Veranstaltung Vertiefung Medizininformatik
int currentFinger;     // Definiert den Messzustand des Systems
enum fingerState {littleFinger= 0, ringFinger,middleFinger,indexFinger,thumb};

//Sensordaten 
int sensoren[] = {SensorInputPin,SensorInputPin1,SensorInputPin2,SensorInputPin3};
int sensoren_length = std::size(sensoren); //das geht seit C++17

EMGFilters myFilter[std::size(sensoren)];
float sensorOffsets[std::size(sensoren)];
// Feedback-LED und Interrupt Variablen
const byte ledPin = 12;
const byte interruptPin = 2;
volatile byte ledState = LOW;
volatile bool messungState = false;

volatile bool WERTE_VORHANDEN = false; // this is used so we can track if we already took samples of every finger
bool abgeschlossene_Finger = false; // this is used to trigger hochzaehlenFinger

//Interrupt (ISR)
void button_Interrupt()
{
  ledState = !ledState;
  messungState = !messungState;
  if (currentFinger == thumb)
      {
        WERTE_VORHANDEN = true;
      }
  else
  {
    WERTE_VORHANDEN = false;
  }
}


bool WERTE_VORHANDEN = false; // this is used so we can track if we already took samples of every finger
unsigned long timeBudget;

int hochzaehlenFinger()
{
  if(currentFinger != thumb)
  {
    currentFinger ++; // ist der currentFinger != Daumen --> wird hochgezaehlt
    return 0;
  }else{ 
    currentFinger = littleFinger;            // anderenfalls wird currentFinger = kleiner Finger gesetzt
    return 1;
  }
}

float messung_sensoren(int sensor, int finger)
{
  
    int rawValue = analogRead(sensor);

    // filter processing
    float filteredValue = myFilter[finger].update(rawValue);

    float correctedValue = filteredValue - sensorOffsets[finger];
  
  return correctedValue;
}

void calibrateSensors(){
  const int calibrationSamples = 3000;
  long sums[sensoren_length] = {0};

  for(int i = 0; i < calibrationSamples; i++){
    unsigned long calibLoopStart = micros();
    for(int j=0; j < sensoren_length;j++){
      int rawValue = analogRead(sensoren[j]);
      int filteredValue = myFilter[j].update(rawValue);
      sums[j] += filteredValue;
    }
    unsigned long calibElapsedTime = micros() - calibLoopStart;
    if(calibElapsedTime < sampleRate) { // Ziel: sampleRate pro Sample
        delayMicroseconds(sampleRate - calibElapsedTime);
    }
  }
    
  // Berechne den durchschnittlichen Offset für jeden Sensor
  for (int i = 0; i < sensoren_length; i++) {
    sensorOffsets[i] = (float)sums[i] / calibrationSamples;
  }
}

Arduino_LED_Matrix matrix;
uint8_t* matrix_feedback[] = {littleFinger_Frame, ringFinger_Frame, middleFinger_Frame, indexFinger_Frame, thumb_Frame};

void setup() {
    /* add setup code here */
    //start Matrix
    matrix.begin();
    matrix.setGrayscaleBits(1);
    matrix.draw(Hi_Frame);

    // setup for time cost measure
    // using micros()
    timeBudget = 1e6 / sampleRate;
    // micros will overflow and auto return to zero every 70 minutes

    // SensorPins konfigurieren, alle als Input
    for(int i=0; i < sensoren_length; i++)
      {
        pinMode(sensoren[i],INPUT);
      }
  
    for(int i=0; i < sensoren_length; i++)
      {
        myFilter[i].init(sampleRate, humFreq, true, true, true);
      }
    calibrateSensors();
    
    // open serial
    Monitor.begin(9600);

    //start Brigde
    Bridge.begin();
    Bridge.provide("hochzaehlenFinger",hochzaehlenFinger); //provide counting of finger for MCU

    //Feedback-LED Setup
    pinMode(ledPin, OUTPUT);
  
    // Mapping der Finger, start Punkt
    currentFinger = littleFinger;
    
    //Interrupt-Setup
    pinMode(interruptPin,INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(interruptPin),button_Interrupt,FALLING); //attachInterrupt(pin, ISR, mode) 
}

void loop() {
    /* add main program code here */
    // In order to make sure the ADC sample frequence on arduino,
    // the time cost should be measured each loop
    /*------------start here-------------------*/

    unsigned long loopStartTime = micros();

    float werte[sensoren_length];
    float werte_raw[sensoren_length];
    float werte_gefiltert[sensoren_length];

    for(int finger = 0; finger < sensoren_length; finger++)
      {
        //werte[finger] = messung_sensoren(sensoren[finger],finger);
        werte_raw[finger] = analogRead(sensoren[finger]);
        werte_gefiltert[finger] = myFilter[finger].update(werte_raw[finger]);
        werte[finger] = werte_gefiltert[finger] - sensorOffsets[finger];
      }
  
    matrix.draw(matrix_feedback[currentFinger]);

    if (messungState) {
      for(int i = 0; i < sensoren_length; i++)
        {
          Bridge.notify("envlope_read",currentFinger,i,werte_raw[i],werte_gefiltert[i],werte[i],sensorOffsets[i]); // Daten an das Python Skript, dabei stellt das i, die Nummerierung der Sensoren da. Angefangen mit 0
        }
      abgeschlossene_Finger = true;
    } else if (abgeschlossene_Finger) {
      if (WERTE_VORHANDEN)
      {
        Bridge.notify("messung_speichern"); 
      }
      hochzaehlenFinger();
      abgeschlossene_Finger = false;
    }
  
    digitalWrite(ledPin,ledState);