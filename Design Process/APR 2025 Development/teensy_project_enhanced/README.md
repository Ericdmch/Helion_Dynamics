# Teensy Wireless Sensor Network Project

## Overview

This project implements a wireless sensor network using two Teensy boards:
- A Teensy 4.0 as a transmitter that collects environmental and motion data
- A Teensy 4.1 as a receiver that forwards the data to a computer

The system uses LoRa communication via Reyax RLYR988 modules for reliable long-range wireless transmission. The collected data is logged and displayed using a cross-platform Python application with Excel integration and data visualization.

## Features

- **Multiple Sensor Integration**: Collects data from BME680 (temperature, humidity, pressure, gas), MPU6050 (acceleration, gyroscope), and photodiode (light level)
- **Long-Range Wireless Communication**: Uses LoRa technology for reliable transmission over long distances
- **Real-Time Data Visualization**: Displays sensor readings in real-time on the computer
- **Excel Integration**: Automatically creates and updates Excel workbooks with formatted data
- **Automated Graph Generation**: Creates various graphs for all sensor data
- **Data Logging**: Stores all sensor data in CSV, JSON, and Excel formats for analysis
- **Cross-Platform Compatibility**: Works on both Windows and Mac operating systems
- **Automatic Port Detection**: Automatically finds the connected Teensy device
- **Signal Quality Monitoring**: Tracks RSSI and SNR for wireless link quality assessment
- **Interactive Dashboard**: Excel dashboard with summary statistics and key visualizations

## Repository Contents

- `teensy_4_0_transmitter.ino`: Arduino code for the Teensy 4.0 transmitter
- `teensy_4_1_receiver.ino`: Arduino code for the Teensy 4.1 receiver
- `teensy_data_logger.py`: Basic Python application for receiving and logging data
- `teensy_data_logger_excel.py`: Enhanced Python application with Excel integration and data visualization
- `test_excel_functionality.py`: Test script for validating Excel functionality with simulated data
- `hardware_setup.md`: Detailed wiring instructions for all components
- `installation_guide.md`: Step-by-step installation and usage instructions
- `code_validation.md`: Analysis of code compatibility and potential issues
- `excel_integration.md`: Documentation for Excel integration features
- `data_visualization_guide.md`: Guide to the data visualization capabilities

## Hardware Requirements

### Teensy 4.0 Transmitter
- Teensy 4.0 board
- Reyax RLYR988 LoRa module
- BME680 environmental sensor
- Analog photodiode module
- MPU6050 accelerometer/gyroscope
- Breadboard and jumper wires
- Power supply (USB or battery)

### Teensy 4.1 Receiver
- Teensy 4.1 board
- Reyax RLYR988 LoRa module
- USB cable for connection to computer

## Software Requirements

- Arduino IDE with Teensyduino add-on
- Required Arduino libraries:
  - Adafruit BME680 Library
  - Adafruit Unified Sensor Library
  - MPU6050_tockn Library
- Python 3.6 or newer
- Python packages:
  - pyserial
  - openpyxl (for Excel integration)
  - matplotlib (for graph generation)
  - pandas (for data analysis)

## Quick Start

1. Set up the hardware according to the wiring instructions in `hardware_setup.md`
2. Install the required software as described in `installation_guide.md`
3. Upload the transmitter code to the Teensy 4.0
4. Upload the receiver code to the Teensy 4.1
5. Connect the Teensy 4.1 to your computer
6. Run the Python logging application:
   - For basic logging: `python teensy_data_logger.py`
   - For Excel integration and graphs: `python teensy_data_logger_excel.py`
7. View real-time data and check the logs directory for saved data and graphs

For detailed instructions, refer to the `installation_guide.md` file.

## Excel Integration

The enhanced logger (`teensy_data_logger_excel.py`) provides comprehensive Excel integration:

- **Automatic Excel Creation**: Creates formatted Excel workbooks with multiple sheets
- **Real-Time Updates**: Updates Excel files as new data is received
- **Dashboard**: Summary statistics and latest readings in an easy-to-read format
- **Embedded Graphs**: Automatically generates and embeds graphs in the Excel file
- **Multiple Data Views**: Separate sheets for different types of data and visualizations

For more details, see `excel_integration.md`.

## Data Visualization

The enhanced logger includes extensive data visualization capabilities:

- **Environmental Graphs**: Temperature, humidity, pressure, and gas resistance over time
- **Motion Graphs**: Acceleration and gyroscope readings with 3D visualization
- **Light Level Graphs**: Photodiode readings over time
- **Combined Dashboards**: Multi-parameter views for comprehensive monitoring

For more details, see `data_visualization_guide.md`.

## Applications

This wireless sensor network can be used for:
- Environmental monitoring
- Home automation
- Weather stations
- Motion and activity tracking
- Remote sensing
- IoT projects
- Educational demonstrations
- Data analysis and visualization

## Customization

The system is designed to be easily customizable:
- Adjust transmission intervals in the transmitter code
- Modify the data format to include additional sensors
- Customize the logging format in the Python application
- Change the LoRa parameters for different range/power requirements
- Modify Excel templates and graph styles to suit your needs

## Troubleshooting

Refer to the troubleshooting section in `installation_guide.md` for solutions to common issues.

## License

This project is provided as open-source software. You are free to modify and distribute it according to your needs.

## Acknowledgments

- The Teensy community for their excellent documentation
- Adafruit for their sensor libraries
- The developers of the MPU6050_tockn library
- The Python community for their tools and libraries
- The openpyxl, matplotlib, and pandas developers for their excellent data visualization tools
