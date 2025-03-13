import serial
import pandas as pd
from datetime import datetime
import os
from pathlib import Path
import time
import sys
import xlsxwriter

# Configuration
TEENSY_PORT = '/dev/tty.usbmodem166453101'  # Change to your Teensy's port
SAMPLE_INTERVAL = 0.1  # seconds
DATA_COLLECTION_TIME = 30  # seconds

def get_desktop_path():
    """Get the user's desktop path in a cross-platform way"""
    home = Path.home()
    desktop = home / 'Desktop'
    return desktop

def setup_serial(port):
    """Set up serial connection to Teensy"""
    try:
        ser = serial.Serial(port, 115200, timeout=0.1)
        print(f"Connected to Teensy on {port}")
        time.sleep(2)  # Wait for Teensy to initialize
        return ser
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        sys.exit(1)

def initialize_data_structures():
    """Initialize data structures"""
    columns = ['Timestamp', 'Seconds Elapsed', 'Raw Value', 'Voltage (V)', 'Light Intensity (%)']
    df = pd.DataFrame(columns=columns)
    return df

def log_data_to_excel(df, desktop_path):
    """Log data to Excel and create charts"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'photodiode_data_{timestamp}.xlsx'
    excel_path = desktop_path / filename
    
    # Create a Pandas Excel writer object
    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        # Write the DataFrame to the Excel file
        df.to_excel(writer, index=False, sheet_name='Data')
        
        # Create a workbook and worksheet for charts
        workbook = writer.book
        worksheet = writer.sheets['Data']
        
        # Create charts
        create_charts(workbook, worksheet, df)
    
    print(f"Data saved to {excel_path}")
    return excel_path

def create_charts(workbook, worksheet, df):
    """Create charts in the Excel file"""
    # Create a chart object
    chart = workbook.add_chart({'type': 'line'})
    
    # Configure the first series (Raw Value)
    chart.add_series({
        'name': 'Raw Value',
        'categories': ['Data', 1, 1, len(df)-1, 1],
        'values': ['Data', 1, 2, len(df)-1, 2],
    })
    
    # Configure the second series (Voltage)
    chart.add_series({
        'name': 'Voltage',
        'categories': ['Data', 1, 1, len(df)-1, 1],
        'values': ['Data', 1, 3, len(df)-1, 3],
    })
    
    # Configure the third series (Light Intensity)
    chart.add_series({
        'name': 'Light Intensity',
        'categories': ['Data', 1, 1, len(df)-1, 1],
        'values': ['Data', 1, 4, len(df)-1, 4],
    })
    
    # Set chart title and axis labels
    chart.set_title({'name': 'Photodiode Data'})
    chart.set_x_axis({'name': 'Seconds Elapsed'})
    chart.set_y_axis({'name': 'Value'})
    
    # Insert the chart into the worksheet
    worksheet.insert_chart('F2', chart)

def main():
    # Get desktop path
    desktop_path = get_desktop_path()
    
    # Setup
    ser = setup_serial(TEENSY_PORT)
    df = initialize_data_structures()
    
    print(f"Starting data acquisition for {DATA_COLLECTION_TIME} seconds. Press Ctrl+C to stop.")
    
    try:
        start_time = time.time()
        while time.time() - start_time < DATA_COLLECTION_TIME:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8').strip()
                    if line:
                        data = process_data_line(line, start_time)
                        if data:
                            df.loc[len(df)] = data
                except UnicodeDecodeError:
                    continue
            time.sleep(SAMPLE_INTERVAL)
            
        # Save data to Excel
        excel_path = log_data_to_excel(df, desktop_path)
        
    except KeyboardInterrupt:
        print("\nData acquisition stopped by user.")
        excel_path = log_data_to_excel(df, desktop_path)
    finally:
        ser.close()
        print("Serial port closed.")

def process_data_line(line, start_time):
    """Process and return data from a single data line"""
    # Expected format: "Raw Value: XXX | Voltage: XX.XXXV | Light Intensity: XX%"
    if line.startswith('Raw Value:'):
        parts = line.split('|')
        if len(parts) != 3:
            return None
        
        try:
            # Extract raw value
            raw_value = int(parts[0].split(': ')[1])
            # Extract voltage
            voltage = float(parts[1].split(': ')[1].split('V')[0])
            # Extract light intensity
            light_intensity = float(parts[2].split(': ')[1].split('%')[0])
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            seconds_elapsed = time.time() - start_time
            
            return [timestamp, seconds_elapsed, raw_value, voltage, light_intensity]
            
        except (ValueError, IndexError) as e:
            print(f"Error processing data line: {line}")
            print(f"Exception: {e}")
            return None
    return None

if __name__ == "__main__":
    main()