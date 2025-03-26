# HRV BIOFEEDBACK

The purpose of this python desktop application is to provide user with HRV based biofeedback. It is developed based on Protocol for Heart Rate Variability Biofeedback Training by Lehrer et al. (2013). The aim of the application is to make biofeedback training more accesible trough wearable devices. 

## Compatible devices
The application was developed and tested with:
- Polar V800 smartwach paired with Polar H10 heart rate sensor
- Windows 11 (ensure Bluetooth connectivity)

## Instalation
The use of a virtual Python environment such as conda or venv is advised. 
The repository can be cloned by running: 
`pip install git+https://github.com/polancka/HRV_biofeedback.git`

Install the necessary libraries: 
`pip install -r requirements.txt`

The application can be started with:
`python main.py`

## User guide
1. Connecting the Polar: 
   - Select button "Connect to a device" and wait for the list to populate with available devices. The Polar should be turned on and on user. 
   - Select the correct device and click button connect.
   - The UI should now show that you are connected to your device.

2. Recording: 
   - Press the button start recording to start recording.
   - Press the button stop recording to stop recording. 

