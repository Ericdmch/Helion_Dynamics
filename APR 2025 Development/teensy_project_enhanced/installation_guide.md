# Installation and Usage Guide (Updated)

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
2. Install the required Python packages using pip:
   ```
   pip install pyserial openpyxl matplotlib pandas
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

### Basic Python Logging Application
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

### Enhanced Python Logging Application with Excel and Graphs
1. Connect the Teensy 4.1 receiver to your computer via USB
2. Open a terminal or command prompt
3. Navigate to the directory containing `teensy_data_logger_excel.py`
4. Run the enhanced application:
   ```
   python teensy_data_logger_excel.py
   ```
5. The application accepts the same command-line arguments as the basic version:
   ```
   python teensy_data_logger_excel.py --list
   python teensy_data_logger_excel.py --port COM3
   python teensy_data_logger_excel.py --directory my_data_logs
   ```

### Excel and Data Visualization Features
- The enhanced logger automatically creates and updates an Excel workbook with multiple sheets:
  - **Sensor Data**: Raw data in tabular format
  - **Dashboard**: Summary statistics and latest readings
  - **Environmental Graphs**: Temperature, humidity, pressure, and gas graphs
  - **Motion Graphs**: Acceleration and gyroscope graphs
  - **Light Graphs**: Light level graphs
- Graphs are automatically generated and embedded in the Excel file
- Graphs are also saved as separate PNG files in the `logs/graphs` directory
- The Excel file is updated every 10 data points by default (configurable in the code)

### Testing Excel Functionality
To test the Excel functionality without actual hardware:
1. Navigate to the directory containing `test_excel_functionality.py`
2. Run the test script:
   ```
   python test_excel_functionality.py
   ```
3. The script will generate simulated sensor data and test the Excel and graph generation capabilities
4. Command-line options:
   ```
   python test_excel_functionality.py --num-samples 50 --delay 0.5 --output-dir test_logs
   ```

## Data Output

### Basic Logger
- Data is displayed in real-time in the terminal
- Data is automatically logged to CSV and JSON files in the `logs` directory
- Press Ctrl+C to stop the application
- Logged data can be found in:
  - `logs/sensor_data.csv` - CSV format for easy import into spreadsheet applications
  - `logs/sensor_data.json` - JSON format for programmatic access

### Enhanced Logger
- All features of the basic logger, plus:
- Excel workbook with formatted data and embedded graphs:
  - `logs/sensor_data.xlsx`
- Graph images in PNG format:
  - `logs/graphs/*.png`

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

### Excel and Graph Issues
- Ensure you have installed all required Python packages: `pyserial`, `openpyxl`, `matplotlib`, and `pandas`
- Check that you have write permissions to the logs directory
- If Excel files are not updating, try closing any open instances of the file
- For large datasets, Excel updates may take longer; be patient during updates

### Python Application Issues
- Verify that Python 3.6 or newer is installed
- Check that all required packages are installed
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
