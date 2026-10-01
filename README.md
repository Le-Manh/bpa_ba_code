# Introduction
This is the source code documentation of the bachelor thesis "Ansteuerung von Handprothesen mit Machine Learning" by Manh Le. The language of the thesis is german. The title roughly translates to: "Control of handprotheses with machine learning". The thesis tried to classify individual finger-movements with emg. 

The thesis used four [DFRobot Gravity:Analog Sensors](https://wiki.dfrobot.com/sen0240/) from OYMotion and the [Arduino Uno Q](https://docs.arduino.cc/hardware/uno-q/) for recording and interference.
Communication of the MCU of Arduino Uno Q and MPU was realized based on: [diy-ecg.uno-Q](https://github.com/diy-ecg/diy-ecg-uno-Q/tree/main)

## data overview (recording)
- Sensors: 4 x [DFRobot Gravity:Analog Sensors](https://wiki.dfrobot.com/sen0240/)
- Sampling rate: 500 Hz
- Lowpass, highpass and notch filter based on OYMotion library in `ArduinoApps/emg_messung/sketch/EMG_Filter/EMGFilters`, used the PR of [edgar-bonet](https://github.com/oymotion/EMGFilters/pull/4) to use multiple sensors
- ADC resolution: 14-Bit
- Sensor Placement see: ´sensor_placement/´

## data overview (train/test data)
- n_subjects: 22
- n_finger-movements: 1250 
- around 56.82 movements per subject
- around 28.41 per hand (left/right)
- more information is written in `auswertung_features/meta.csv`

# model overview
Tested:
- Support Vector machine (SVM) 
- Random Forest (RF) 
- Multi-Layer Perceptrons (MLP)

Verified with a Leave-One-Group-Out-Cross-Validation (LOGO-CV). The group was the different subjects.
MLP was also tuned with a parameter-grid, which can be found in `ANN/gridsearch_mlp.py` line 139 to 145

# directory structure explanantion

## ANN
This folder holds every search and test of the mlp. The `debug.ipynb` was used to test plots or test models if it really is working
The gridsearch was run in `gridsearch_mlp.py`

## ArduinoApps
This directory has the structure of the Apps and is build how the Arduino Uno Q expects it. `diy-ecg-uno-q` is as reference for bridge communication as a submodule in the repository. `emg_auswertung` is the recording with `sketch` for the MCU side and `python` for teh MPU side. More informationcan be found in [emg_auswertung/README.md](ArduinoApps/emg_auswertung/README.md)
