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

#define TIMING_DEBUG 0

#define SensorInputPin A0 // input pin number
#define SensorInputPin1 A1 // input pin number
#define SensorInputPin2 A2 // input pin number
#define SensorInputPin3 A3 // input pin number

#include "Arduino_RouterBridge.h"

EMGFilters myFilter;
// discrete filters must works with fixed sample frequence
// our emg filter only support "SAMPLE_FREQ_500HZ" or "SAMPLE_FREQ_1000HZ"
// other sampleRate inputs will bypass all the EMG_FILTER
int sampleRate = SAMPLE_FREQ_1000HZ;
// For countries where power transmission is at 50 Hz
// For countries where power transmission is at 60 Hz, need to change to
// "NOTCH_FREQ_60HZ"
// our emg filter only support 50Hz and 60Hz input
// other inputs will bypass all the EMG_FILTER
int humFreq = NOTCH_FREQ_50HZ;

//Aus der Veranstaltung Vertiefung Medizininformatik
int currentFinger;     // Definiert den Messzustand des Systems
enum fingerState {littleFinger= 0, ringFinger,middleFinger,indexFinger,thumb};

//Sensordaten 
int sensoren[4] = {SensorInputPin,SensorInputPin1,SensorInputPin2,SensorInputPin3};
int sensoren_length = std::size(sensoren); //das geht seit C++17

// Feedback-LED und Interrupt Variablen
const byte ledPin = 12;
const byte interruptPin = 2;
volatile byte ledState = LOW;
volatile bool messungState = false;

//Interrupt (ISR)
void button_Interrupt()
{
  ledState = !ledState;
  messungState = !messungState;
}

bool WERTE_VORHANDEN = false;

// Calibration:
// put on the sensors, and release your muscles;
// wait a few seconds, and select the max value as the throhold;
// any value under throhold will be set to zero
static int Throhold = 600;

unsigned long timeStamp;
unsigned long timeBudget;

void hochzaehlenFinger()
{
  if(currentFinger != thumb)  currentFinger ++; // ist der currentFinger != Daumen --> wird hochgezaehlt
  else currentFinger = littleFinger;            // anderenfalls wird currentFinger = kleiner Finger gesetzt
}

int messung_sensoren(int sensor)
{
  
    int Value = analogRead(sensor);

    // filter processing
    int DataAfterFilter = myFilter.update(Value);

    int envlope = sq(DataAfterFilter);
    
    // any value under throhold will be set to zero
    envlope = (envlope > Throhold) ? envlope : 0;
    
  return envlope;
}


void setup() {
    /* add setup code here */
      
    myFilter.init(sampleRate, humFreq, true, true, true);

    // open serial
    Monitor.begin(9600);

    //start Brigde
    Bridge.begin();
    Bridge.provide("hochzaehlenFinger",hochzaehlenFinger); //provide counting of finger for MCU
    
    // setup for time cost measure
    // using micros()
    timeBudget = 1e6 / sampleRate;
    // micros will overflow and auto return to zero every 70 minutes

    //Feedback-LED Setup
    pinMode(ledPin, OUTPUT);

    // SensorPins konfigurieren, alle als Input
    for(int i=0; i < sensoren_length; i++)
      {
        pinMode(sensoren[i],INPUT);
      }
  
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
    timeStamp = micros();
      
    int werte[sensoren_length];
    for(int i = 0; i < sensoren_length; i++)
      {
        werte[i] = messung_sensoren(sensoren[i]);
      }
  
    timeStamp = micros() - timeStamp;
    if (TIMING_DEBUG) {
        // Serial.print("Read Data: "); Serial.println(Value);
        //Monitor.print("Filtered Data: ");Monitor.println(DataAfterFilter);
        Monitor.print("Squared Data: ");
        Monitor.println(werte[0]);
        //Monitor.print("Filters cost time: "); Monitor.println(timeStamp);
        // the filter cost average around 520 us  
    }
  
    if (messungState) {
      Bridge.call("messung",true);
      for(int i = 0; i < sensoren_length; i++)
        {
          Bridge.call("envlope_read",currentFinger,i,werte[i]); // Daten an das Python Skript
        }
      WERTE_VORHANDEN = true;
    } else {
      Bridge.call("messung",false);
      Bridge.call("messung_speichern", WERTE_VORHANDEN);
      WERTE_VORHANDEN = false;
    }
    digitalWrite(ledPin,ledState);
    

  
    /*------------end here---------------------*/
    // if less than timeBudget, then you still have (timeBudget - timeStamp) to
    // do your work
    delayMicroseconds(500);
    // if more than timeBudget, the sample rate need to reduce to
    // SAMPLE_FREQ_500HZ
}
