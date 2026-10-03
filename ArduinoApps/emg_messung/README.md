# 😀 EMG_Messung
This app is part of the bachelor thesis "Ansteuerung von Handprothesen mit Machine Learning" by Manh Le. It uses four [DFRobot Gravity:Analog Sensors](https://wiki.dfrobot.com/sen0240/) from OYMotion to get the emg signals which will be written into a csv file in [`python/messdaten`](python/messdaten). The csv files will be named in Regex-terms: "messung_\[lr\]_\[0-9\]+".csv with "Aktueller Finger,timestamp_ms,sensor_0,sensor_1,sensor_2,sensor_3" as headers. The first column is the label of the finger, the timestap in ms as the second coilumn, every column after that is the value of the sensor at that timestamp_ms. One csv file has the finger movement from the little finger (0) to the thumb (4) and always in this way. In Python dictionary terms the key-value pair looks like this: `{0 : "little Finger", 1: "ringfinger", 2: "middle finger", 3:"index finger", 4:"thumb"}` and the labels would change like a for-loop enumerated through the keys.

## MCU/sketch side
Used pins: 
- A1, A2, A3 and A4 are reserved for the emg sensors as analog inputs
- 12 as Led pin
- 2 as interrupt pin for the button to start and stop the recording
- 6 as the button to document which hand is recorded. The program will start with the right hand as default.

The recording works by starting the MCU an drawing a "HI" on the LED-Matrix and if it's ready it will be draw a "RD". After activating the interrupt button the LED will be lit up to indicate a recording. The next click on the button will stop the recording and the LED will turn off. While the LED is lit up the data of the emg sensors will be written into a ringbuffer as serialized bytes with a CRC-16 Checksum and an overflow flag. The overflow flag is '0x21' which is the ASCII Symbol for "!". Also the ringbuffer will be read from the MPU side. The other Button changes the state of the variable `rightHand` to true or false. Every time the recording starts this state will be send to the MPU and documents the which hand is being recorded. This way every recording can change the hand. 

Overview of MCU side:
- 4 sensors
- ADC resolution: 14 Bit
- Sampling Rate: 500 Hz, the library of OYMotion would also allow 1000 Hz

## MPU/ python side
If the MPU gets the information that the MCU is recoding the deserializing of the ringbuffer will be activated and send through the Arduino Bridge. At this side the values will be flushed into a file after deserialization and checking the checksum. The MPU will read which number the last written csv had in [`last_measurement.txt `](python/messdaten/last_measurement.txt) and will add one. The information of the recording will also give the information of the hand. This will be documented in the filename with "l" for left or "r" for right.
