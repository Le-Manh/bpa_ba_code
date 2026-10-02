# 🐢 EMG_Auswertung
This app is part of the bachelor thesis "Ansteuerung von Handprothesen mit Machine Learning" by Manh Le. It used the trained MLP-Models on the MPU side to categorize finger-movements with emg. The Model is able to return probabilities for each finger but will only return an int. This int will be send through the Arduino Uno Q Bridge where the MCU side can draw the symbol for each finger. The finger are categorized this way: {0 : "little Finger", 1: "ringfinger", 2: "middle finger", 3:"index finger", 4:"thumb"}. 

## MCU/Sketch side
Used pins:
- A1, A2, A3 and A4 are reserved for the emg sensors as analog inputs
- 12 as Led pin
- 2 as interrupt pin for the button to start and stop the recording

The recording works by starting the MCU and drawing a "HI" on the LED-Matrix. After activating the interrupt button the LED will be lit up to indicate a recording. The next click on the button will stop the recording and the LED will turn off. While the LED is lit up the data of the emg sensors will be written into a ringbuffer as serialized bytes with a CRC-16 Checksum and an overflow flag. The overflow flag is '0x21' which is the ASCII Symbol for "!". Also the ringbuffer will be read from the MPU side. 

Overview of MCU side:
- 4 sensors
- ADC resolution: 14 Bit
- Sampling Rate: 500 Hz, the library of OYMotion would also allow 1000 Hz

## MPU/python side
If the MPU side is ready the LED Matrix will show "RD". The MCU is always faster to start than the MPU. If the MPU gets the information that the MCU is recoding the deserializing of the ringbuffer will be activated. These data will be filled into an dictionary with "sensor_i" with i as number of sensors starting with 0. After being transformed into an dataframe the data will be feed into tsfel and the features will be build. The model is only imported for the right hand for now. 
