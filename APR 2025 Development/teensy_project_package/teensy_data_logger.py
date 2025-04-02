#!/usr/bin/env python3
"""
Teensy Data Logger

This Python application receives data from a Teensy 4.1 via serial connection,
processes it, and logs it to a file. It's designed to work on both Mac and Windows.

The data includes:
- BME680 environmental sensor readings (temperature, humidity, pressure, gas)
- Analog photodiode module readings
- MPU6050 accelerometer/gyroscope readings
"""

import serial
import serial.tools.list_ports
import time
import datetime
import csv
import os
import argparse
import platform
import json
import threading
import sys
from pathlib import Path

# Default settings
DEFAULT_BAUD_RATE = 115200
DEFAULT_LOG_DIR = "logs"
DEFAULT_CSV_FILENAME = "sensor_data.csv"
DEFAULT_JSON_FILENAME = "sensor_data.json"

class TeensyDataLogger:
    def __init__(self, port=None, baud_rate=DEFAULT_BAUD_RATE, log_dir=DEFAULT_LOG_DIR):
        """Initialize the Teensy Data Logger."""
        self.port = port
        self.baud_rate = baud_rate
        self.log_dir = log_dir
        self.serial_connection = None
        self.running = False
        self.data_count = 0
        
        # Create log directory if it doesn't exist
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize CSV file with headers
        self.csv_path = os.path.join(log_dir, DEFAULT_CSV_FILENAME)
        self.json_path = os.path.join(log_dir, DEFAULT_JSON_FILENAME)
        
        # Check if CSV file exists, if not create it with headers
        csv_exists = os.path.isfile(self.csv_path)
        with open(self.csv_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if not csv_exists:
                writer.writerow([
                    'Timestamp', 'Local Time', 'Device Time (ms)', 'Sender Address', 
                    'RSSI', 'SNR', 'Temperature (°C)', 'Pressure (hPa)', 'Humidity (%)', 
                    'Gas Resistance (kOhms)', 'AccelX (g)', 'AccelY (g)', 'AccelZ (g)', 
                    'GyroX (°/s)', 'GyroY (°/s)', 'GyroZ (°/s)', 'Light Level'
                ])
    
    def find_teensy_port(self):
        """Automatically find the Teensy serial port."""
        system = platform.system()
        ports = list(serial.tools.list_ports.comports())
        
        for port in ports:
            # Look for Teensy in the description
            if "Teensy" in port.description:
                return port.device
            
            # On Mac, Teensy often appears as "usbmodem"
            if system == "Darwin" and "usbmodem" in port.device:
                return port.device
                
            # On Windows, check for specific VID:PID combinations
            if system == "Windows" and hasattr(port, 'vid') and hasattr(port, 'pid'):
                # Teensy 4.1 VID:PID is typically 0x16C0:0x0483
                if port.vid == 0x16C0 and port.pid == 0x0483:
                    return port.device
        
        return None
    
    def connect(self):
        """Connect to the Teensy device."""
        if not self.port:
            self.port = self.find_teensy_port()
            if not self.port:
                raise Exception("Teensy device not found. Please specify port manually.")
        
        try:
            self.serial_connection = serial.Serial(self.port, self.baud_rate, timeout=1)
            print(f"Connected to Teensy on {self.port} at {self.baud_rate} baud")
            return True
        except serial.SerialException as e:
            print(f"Error connecting to Teensy: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the Teensy device."""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("Disconnected from Teensy")
    
    def parse_data(self, data_string):
        """Parse the data string received from Teensy."""
        # Expected format: TIME:123456,ADDR:1,RSSI:-80,SNR:10,T:25.50,P:1013.25,H:45.20,G:100.50,AX:0.10,AY:0.20,AZ:0.98,GX:1.50,GY:2.50,GZ:0.50,L:512
        data_dict = {}
        
        # Split by comma and process each key-value pair
        for item in data_string.split(','):
            if ':' in item:
                key, value = item.split(':', 1)
                try:
                    # Try to convert to float if possible
                    data_dict[key] = float(value)
                except ValueError:
                    # Keep as string if not a number
                    data_dict[key] = value
        
        return data_dict
    
    def log_data(self, data_dict):
        """Log the parsed data to CSV and JSON files."""
        timestamp = time.time()
        local_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Log to CSV
        with open(self.csv_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                timestamp,
                local_time,
                data_dict.get('TIME', ''),
                data_dict.get('ADDR', ''),
                data_dict.get('RSSI', ''),
                data_dict.get('SNR', ''),
                data_dict.get('T', ''),
                data_dict.get('P', ''),
                data_dict.get('H', ''),
                data_dict.get('G', ''),
                data_dict.get('AX', ''),
                data_dict.get('AY', ''),
                data_dict.get('AZ', ''),
                data_dict.get('GX', ''),
                data_dict.get('GY', ''),
                data_dict.get('GZ', ''),
                data_dict.get('L', '')
            ])
        
        # Log to JSON (append to JSON array)
        json_entry = {
            'timestamp': timestamp,
            'local_time': local_time,
            'data': data_dict
        }
        
        # Append to JSON file
        with open(self.json_path, 'a') as jsonfile:
            jsonfile.write(json.dumps(json_entry) + '\n')
        
        self.data_count += 1
        return True
    
    def display_data(self, data_dict):
        """Display the parsed data in a readable format."""
        print("\n--- Received Data ---")
        print(f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Device Time: {data_dict.get('TIME', 'N/A')} ms")
        print(f"Sender: {data_dict.get('ADDR', 'N/A')}")
        print(f"Signal: RSSI={data_dict.get('RSSI', 'N/A')} dBm, SNR={data_dict.get('SNR', 'N/A')} dB")
        print("\nEnvironmental Data (BME680):")
        print(f"  Temperature: {data_dict.get('T', 'N/A')} °C")
        print(f"  Pressure: {data_dict.get('P', 'N/A')} hPa")
        print(f"  Humidity: {data_dict.get('H', 'N/A')} %")
        print(f"  Gas Resistance: {data_dict.get('G', 'N/A')} kOhms")
        print("\nMotion Data (MPU6050):")
        print(f"  Acceleration: X={data_dict.get('AX', 'N/A')}, Y={data_dict.get('AY', 'N/A')}, Z={data_dict.get('AZ', 'N/A')} g")
        print(f"  Gyroscope: X={data_dict.get('GX', 'N/A')}, Y={data_dict.get('GY', 'N/A')}, Z={data_dict.get('GZ', 'N/A')} °/s")
        print("\nLight Data (Photodiode):")
        print(f"  Light Level: {data_dict.get('L', 'N/A')}")
        print(f"Total records: {self.data_count}")
        print("---------------------")
    
    def start_logging(self):
        """Start the logging process."""
        if not self.serial_connection or not self.serial_connection.is_open:
            if not self.connect():
                return False
        
        self.running = True
        print("Logging started. Press Ctrl+C to stop.")
        
        try:
            while self.running:
                if self.serial_connection.in_waiting:
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    if line:
                        try:
                            data_dict = self.parse_data(line)
                            if data_dict:
                                self.log_data(data_dict)
                                self.display_data(data_dict)
                        except Exception as e:
                            print(f"Error processing data: {e}")
                            print(f"Raw data: {line}")
                time.sleep(0.01)  # Small delay to prevent CPU hogging
        except KeyboardInterrupt:
            print("\nLogging stopped by user")
        except Exception as e:
            print(f"Error during logging: {e}")
        finally:
            self.running = False
            self.disconnect()
        
        return True

def list_serial_ports():
    """List all available serial ports."""
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found")
        return
    
    print("\nAvailable serial ports:")
    for i, port in enumerate(ports):
        print(f"{i+1}. {port.device} - {port.description}")

def main():
    """Main function to parse arguments and start the logger."""
    parser = argparse.ArgumentParser(description='Teensy Data Logger')
    parser.add_argument('-p', '--port', help='Serial port to connect to')
    parser.add_argument('-b', '--baud', type=int, default=DEFAULT_BAUD_RATE, help='Baud rate')
    parser.add_argument('-d', '--directory', default=DEFAULT_LOG_DIR, help='Log directory')
    parser.add_argument('-l', '--list', action='store_true', help='List available serial ports')
    
    args = parser.parse_args()
    
    if args.list:
        list_serial_ports()
        return
    
    logger = TeensyDataLogger(port=args.port, baud_rate=args.baud, log_dir=args.directory)
    
    try:
        logger.start_logging()
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        logger.disconnect()

if __name__ == "__main__":
    main()
