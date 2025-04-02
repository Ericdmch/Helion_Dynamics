# Teensy Project - Installation and Usage Guide

## Software Requirements

### Arduino IDE Setup
1. Download and install the Arduino IDE from [arduino.cc](https://www.arduino.cc/en/software)
2. Install Teensyduino from [PJRC](https://www.pjrc.com/teensy/td_download.html)
3. Open Arduino IDE and select the appropriate Teensy board from Tools > Board menu

### Required Arduino Libraries
Install the following libraries using the Arduino Library Manager (Sketch > Include Library > Manage Libraries):
1. Adafruit BME680 Library
2. Adafruit Unified Sensor Library
3. MPU6050_tockn Library

### Python Setup
1. Install Python 3.6 or newer from [python.org](https://www.python.org/downloads/)
2. Install the required Python package using pip:
   ```
   pip install pyserial
   ```

## Hardware Setup
Refer to the `hardware_setup.md` file for detailed wiring instructions.

## Installation Instructions

### Teensy 4.0 Transmitter
1. Connect your Teensy 4.0 to your computer via USB
2. Open the `teensy_4_0_transmitter.ino` file in Arduino IDE
3. Select "Teensy 4.0" from the Tools > Board menu
4. Click the Upload button to program the Teensy 4.0
5. After uploading, you can open the Serial Monitor (115200 baud) to verify the transmitter is working

### Teensy 4.1 Receiver
1. Connect your Teensy 4.1 to your computer via USB
2. Open the `teensy_4_1_receiver.ino` file in Arduino IDE
3. Select "Teensy 4.1" from the Tools > Board menu
4. Click the Upload button to program the Teensy 4.1
5. After uploading, you can open the Serial Monitor (115200 baud) to verify the receiver is working

### Python Logging Application
1. Connect the Teensy 4.1 receiver to your computer via USB
2. Open a terminal or command prompt
3. Navigate to the directory containing `teensy_data_logger.py`
4. Run the application:
   ```
   python teensy_data_logger.py
   ```
5. If the serial port is not automatically detected, you can list available ports:
   ```
   python teensy_data_logger.py --list
   ```
6. Specify a port manually if needed:
   ```
   python teensy_data_logger.py --port COM3  # Windows example
   python teensy_data_logger.py --port /dev/tty.usbmodem12345  # Mac example
   ```

## Usage Instructions

### Teensy 4.0 Transmitter
- Once programmed, the Teensy 4.0 will automatically start collecting sensor data and transmitting it via the LoRa module
- The transmitter sends data every 1 second by default (this can be adjusted in the code)
- The onboard LED will blink with each transmission
- For portable use, you can power the Teensy 4.0 with a battery

### Teensy 4.1 Receiver
- Once programmed, the Teensy 4.1 will automatically start listening for data from the transmitter
- When data is received, it will be forwarded to the computer via USB serial
- The onboard LED will blink when data is received

### Python Logging Application
- The application will display received data in real-time in the terminal
- Data is automatically logged to CSV and JSON files in the `logs` directory
- Press Ctrl+C to stop the application
- Logged data can be found in:
  - `logs/sensor_data.csv` - CSV format for easy import into spreadsheet applications
  - `logs/sensor_data.json` - JSON format for programmatic access

## Troubleshooting

### No Data Transmission
- Verify that both LoRa modules are powered and connected correctly
- Check that the LoRa modules are configured with the same parameters (frequency, spreading factor, etc.)
- Ensure the transmitter and receiver are within range of each other
- Check the power supply to the Teensy 4.0 transmitter

### Serial Communication Issues
- Verify that the correct serial port is being used
- Check that the baud rate is set to 115200
- Ensure the USB cable is a data cable, not just a charging cable
- Try a different USB port or cable

### Sensor Reading Issues
- Verify that all sensors are correctly wired
- Check the I2C addresses if multiple I2C devices are used
- Ensure the sensors are powered with the correct voltage (3.3V for most sensors)

### Python Application Issues
- Verify that Python 3.6 or newer is installed
- Check that the pyserial package is installed
- Ensure you have write permissions to the logs directory
- On some systems, you may need to run the application with administrator/sudo privileges

## Data Format

The data transmitted between the Teensy 4.0 and Teensy 4.1 follows this format:
```
T:{temp},P:{press},H:{hum},G:{gas},AX:{accX},AY:{accY},AZ:{accZ},GX:{gyroX},GY:{gyroY},GZ:{gyroZ},L:{light}
```

The data sent from the Teensy 4.1 to the computer follows this format:
```
TIME:{device_time},ADDR:{sender_address},RSSI:{rssi},SNR:{snr},T:{temp},P:{press},H:{hum},G:{gas},AX:{accX},AY:{accY},AZ:{accZ},GX:{gyroX},GY:{gyroY},GZ:{gyroZ},L:{light}
```

Where:
- `{device_time}` is the milliseconds since the Teensy 4.1 started
- `{sender_address}` is the address of the transmitter (1)
- `{rssi}` is the Received Signal Strength Indicator in dBm
- `{snr}` is the Signal-to-Noise Ratio in dB
- `{temp}` is the temperature in °C
- `{press}` is the atmospheric pressure in hPa
- `{hum}` is the relative humidity in %
- `{gas}` is the gas resistance in kOhms
- `{accX/Y/Z}` are the acceleration values in g
- `{gyroX/Y/Z}` are the gyroscope values in °/s
- `{light}` is the light level from the photodiode (0-1023)
