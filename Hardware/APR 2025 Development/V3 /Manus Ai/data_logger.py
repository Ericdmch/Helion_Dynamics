"""
Data Logging to Excel Script
- Receives data from Teensy 4.1 via USB serial
- Processes and formats the data
- Creates and updates an Excel file
"""
import serial
import time
import json
import os
import sys
import pandas as pd
from datetime import datetime
import argparse

def setup_serial(port, baud_rate=115200, timeout=1):
    """
    Set up serial connection to Teensy 4.1
    
    Args:
        port: Serial port (e.g., 'COM3' on Windows, '/dev/ttyACM0' on Linux)
        baud_rate: Baud rate for serial communication
        timeout: Read timeout in seconds
        
    Returns:
        Serial object if successful, None otherwise
    """
    try:
        ser = serial.Serial(port, baud_rate, timeout=timeout)
        print(f"Connected to {port} at {baud_rate} baud")
        return ser
    except Exception as e:
        print(f"Error connecting to serial port: {e}")
        return None

def read_data_from_serial(ser):
    """
    Read data from serial port, looking for data between DATA_BEGIN and DATA_END markers
    
    Args:
        ser: Serial object
        
    Returns:
        JSON data if successful, None otherwise
    """
    try:
        # Wait for the DATA_BEGIN marker
        line = ser.readline().decode('utf-8', 'ignore').strip()
        while line != "DATA_BEGIN":
            line = ser.readline().decode('utf-8', 'ignore').strip()
            if not line:  # Empty line
                time.sleep(0.1)
                continue
        
        # Read the JSON data
        data_line = ser.readline().decode('utf-8', 'ignore').strip()
        
        # Wait for the DATA_END marker
        line = ser.readline().decode('utf-8', 'ignore').strip()
        while line != "DATA_END":
            line = ser.readline().decode('utf-8', 'ignore').strip()
            if not line:  # Empty line
                time.sleep(0.1)
                continue
        
        # Parse the JSON data
        data = json.loads(data_line)
        return data
    except Exception as e:
        print(f"Error reading data from serial: {e}")
        return None

def process_data(data):
    """
    Process and format the received data
    
    Args:
        data: Dictionary containing sensor data
        
    Returns:
        Processed data dictionary with formatted values
    """
    processed = {}
    
    # Add timestamp
    processed['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Process Teensy 4.0 data
    if 't40_temperature' in data:
        processed['t40_temperature_c'] = data['t40_temperature']
        processed['t40_temperature_f'] = (data['t40_temperature'] * 9/5) + 32
    
    if 't40_humidity' in data:
        processed['t40_humidity_pct'] = data['t40_humidity']
    
    if 't40_pressure' in data:
        processed['t40_pressure_hpa'] = data['t40_pressure']
        processed['t40_pressure_inhg'] = data['t40_pressure'] * 0.02953
    
    if 't40_gas' in data:
        processed['t40_gas_ohm'] = data['t40_gas']
    
    if 't40_altitude' in data:
        processed['t40_altitude_m'] = data['t40_altitude']
        processed['t40_altitude_ft'] = data['t40_altitude'] * 3.28084
    
    # Process accelerometer and gyroscope data
    if all(k in data for k in ['t40_accel_x', 't40_accel_y', 't40_accel_z']):
        processed['t40_accel_x_ms2'] = data['t40_accel_x']
        processed['t40_accel_y_ms2'] = data['t40_accel_y']
        processed['t40_accel_z_ms2'] = data['t40_accel_z']
        
        # Calculate total acceleration magnitude
        accel_mag = (data['t40_accel_x']**2 + data['t40_accel_y']**2 + data['t40_accel_z']**2)**0.5
        processed['t40_accel_magnitude_ms2'] = accel_mag
    
    if all(k in data for k in ['t40_gyro_x', 't40_gyro_y', 't40_gyro_z']):
        processed['t40_gyro_x_rads'] = data['t40_gyro_x']
        processed['t40_gyro_y_rads'] = data['t40_gyro_y']
        processed['t40_gyro_z_rads'] = data['t40_gyro_z']
    
    # Process GPS data
    if all(k in data for k in ['t40_latitude', 't40_longitude']):
        processed['t40_latitude'] = data['t40_latitude']
        processed['t40_longitude'] = data['t40_longitude']
        
        # Format as degrees, minutes, seconds
        lat_deg = int(abs(data['t40_latitude']))
        lat_min = int((abs(data['t40_latitude']) - lat_deg) * 60)
        lat_sec = ((abs(data['t40_latitude']) - lat_deg) * 60 - lat_min) * 60
        lat_dir = 'N' if data['t40_latitude'] >= 0 else 'S'
        
        lon_deg = int(abs(data['t40_longitude']))
        lon_min = int((abs(data['t40_longitude']) - lon_deg) * 60)
        lon_sec = ((abs(data['t40_longitude']) - lon_deg) * 60 - lon_min) * 60
        lon_dir = 'E' if data['t40_longitude'] >= 0 else 'W'
        
        processed['t40_position'] = f"{lat_deg}°{lat_min}'{lat_sec:.2f}\"{lat_dir}, {lon_deg}°{lon_min}'{lon_sec:.2f}\"{lon_dir}"
    
    # Process light sensor data
    if 't40_light' in data:
        processed['t40_light_raw'] = data['t40_light']
        processed['t40_light_percent'] = (data['t40_light'] / 65535) * 100
    
    # Process Teensy 4.1 data
    if 't41_temperature' in data:
        processed['t41_temperature_c'] = data['t41_temperature']
        processed['t41_temperature_f'] = (data['t41_temperature'] * 9/5) + 32
    
    if 't41_humidity' in data:
        processed['t41_humidity_pct'] = data['t41_humidity']
    
    if 't41_pressure' in data:
        processed['t41_pressure_hpa'] = data['t41_pressure']
        processed['t41_pressure_inhg'] = data['t41_pressure'] * 0.02953
    
    if 't41_gas' in data:
        processed['t41_gas_ohm'] = data['t41_gas']
    
    if 't41_altitude' in data:
        processed['t41_altitude_m'] = data['t41_altitude']
        processed['t41_altitude_ft'] = data['t41_altitude'] * 3.28084
    
    # Process Teensy 4.1 GPS data
    if all(k in data for k in ['t41_latitude', 't41_longitude']):
        processed['t41_latitude'] = data['t41_latitude']
        processed['t41_longitude'] = data['t41_longitude']
        
        # Format as degrees, minutes, seconds
        lat_deg = int(abs(data['t41_latitude']))
        lat_min = int((abs(data['t41_latitude']) - lat_deg) * 60)
        lat_sec = ((abs(data['t41_latitude']) - lat_deg) * 60 - lat_min) * 60
        lat_dir = 'N' if data['t41_latitude'] >= 0 else 'S'
        
        lon_deg = int(abs(data['t41_longitude']))
        lon_min = int((abs(data['t41_longitude']) - lon_deg) * 60)
        lon_sec = ((abs(data['t41_longitude']) - lon_deg) * 60 - lon_min) * 60
        lon_dir = 'E' if data['t41_longitude'] >= 0 else 'W'
        
        processed['t41_position'] = f"{lat_deg}°{lat_min}'{lat_sec:.2f}\"{lat_dir}, {lon_deg}°{lon_min}'{lon_sec:.2f}\"{lon_dir}"
    
    # Add signal quality metrics if available
    if 'rssi' in data:
        processed['rssi_dbm'] = data['rssi']
    
    if 'snr' in data:
        processed['snr_db'] = data['snr']
    
    return processed

def update_excel(data, excel_file):
    """
    Update Excel file with new data
    
    Args:
        data: Processed data dictionary
        excel_file: Path to Excel file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Convert data to DataFrame
        df_new = pd.DataFrame([data])
        
        # Check if file exists
        if os.path.exists(excel_file):
            # Read existing data
            df_existing = pd.read_excel(excel_file)
            
            # Append new data
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new
        
        # Write to Excel file
        df_combined.to_excel(excel_file, index=False)
        print(f"Data saved to {excel_file}")
        return True
    except Exception as e:
        print(f"Error updating Excel file: {e}")
        return False

def main():
    """Main function to run the data logging script"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Log Teensy sensor data to Excel')
    parser.add_argument('--port', type=str, required=True, help='Serial port (e.g., COM3 on Windows, /dev/ttyACM0 on Linux)')
    parser.add_argument('--baud', type=int, default=115200, help='Baud rate (default: 115200)')
    parser.add_argument('--output', type=str, default='sensor_data.xlsx', help='Output Excel file (default: sensor_data.xlsx)')
    parser.add_argument('--interval', type=float, default=0, help='Logging interval in seconds (default: 0, log as fast as possible)')
    args = parser.parse_args()
    
    # Set up serial connection
    ser = setup_serial(args.port, args.baud)
    if not ser:
        sys.exit(1)
    
    print(f"Logging data to {args.output} (Press Ctrl+C to stop)")
    
    try:
        while True:
            # Read data from serial
            data = read_data_from_serial(ser)
            if data:
                # Process data
                processed_data = process_data(data)
                
                # Update Excel file
                update_excel(processed_data, args.output)
            
            # Wait for the specified interval
            if args.interval > 0:
                time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Logging stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if ser:
            ser.close()
            print("Serial connection closed")

if __name__ == "__main__":
    main()
