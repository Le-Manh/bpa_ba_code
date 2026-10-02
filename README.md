# Introduction
This is the source code documentation of the bachelor thesis "Ansteuerung von Handprothesen mit Machine Learning" by Manh Le. The language of the thesis is german. The title roughly translates to: "Control of handprotheses with machine learning". The thesis tried to classify individual finger-movements with emg. 

The thesis used four [DFRobot Gravity:Analog Sensors](https://wiki.dfrobot.com/sen0240/) from OYMotion and the [Arduino Uno Q](https://docs.arduino.cc/hardware/uno-q/) for recording and interference.
Communication of the MCU of Arduino Uno Q and MPU was realized based on: [diy-ecg.uno-Q](https://github.com/diy-ecg/diy-ecg-uno-Q/tree/main)

## data overview (recording)
- Sensors: 4 x [DFRobot Gravity:Analog Sensors](https://wiki.dfrobot.com/sen0240/)
- Sampling rate: 500 Hz
- Lowpass, highpass and notch filter based on OYMotion library in `ArduinoApps/emg_messung/sketch/EMG_Filter/EMGFilters/`, implemented the PR of [edgar-bonet](https://github.com/oymotion/EMGFilters/pull/4) to use multiple sensors
- ADC resolution: 14-Bit
- Sensor Placement see: `sensor_placement/`

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
This directory has the structure of the Apps and is build how the Arduino Uno Q expects it. 
- `diy-ecg-uno-q/` is as reference for bridge communication as a submodule in the repository. 
- `emg_messung/` is the recording with `sketch/` for the MCU side and `python/` for the MPU side. More information can be found in [emg_messung/README.md](ArduinoApps/emg_messung/README.md)
- `emg_auswertung/` is the interference with `sketch/` for the MCU side and `python/` for the MPU side. More information can be found in [emg_auswertung/README.md](ArduinoApps/emg_auswertung/README.md)
The raw data of the recording is in [`emg_messung/python/messdaten/`](ArduinoApps/emg_messung/python/messdaten/). 

## auswertung_features
This directory has the results and visualization of the LOGO for SVM, RF and MLP. The raw results of the python scripts can be found in `results/`
- `results/` is the directory with results as raw numbers as csv files.
- `result_plots/` is the directory of different plots like a normalized CM and Violinplots of the LOGO-Runs
This directory has also the [`meta.csv`](auswertung_features/meta.csv) which holds the information of which csv file as relative path of the recording matches which subject and which hand. It also has the session date.
The directory `cache/` is not part of the repo but is existing here. It holds the dataframe of tsfel after the feature extraction as csv. This way it does not need to be build every time and saves a lot of time.

## auswertung_plots
This directory is part of the project before the main-thesis. It was used to visualize the filtered data of the recording.

## KI-Hilfen
This directory has every conversation with AI I hold to document what I really did.

## medizininformatik
This is a submodule is part of a course in the University "HAWK Hochschule für angewandte Wissenschaft und Kunst Hildesheim/Holzminden/Göttingen". This is only in here as an reference for myself.

## sensor_placement
This directory has the pictures to visualize the sensor placements
