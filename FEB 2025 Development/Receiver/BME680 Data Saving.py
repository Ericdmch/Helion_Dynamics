import serial
import time
import os
from openpyxl import Workbook

# Establish serial connection with Arduino
arduino_port = '/dev/cu.usbserial-A10LVGB2'  # Replace with your Arduino port
baud_rate = 115200

try:
    ser = serial.Serial(arduino_port, baud_rate)
    print(f"Connected to {arduino_port} at {baud_rate} baud.")
except serial.SerialException as e:
    print(f"Failed to connect to {arduino_port}: {e}")
    exit(1)

# Create an Excel workbook and sheet
wb = Workbook()
ws = wb.active
ws.title = "Sensor Data"
ws.append(["Timestamp", "Temperature (C)", "Pressure (hPa)", "Humidity (%)", "Gas Resistance (KOhms)"])

# Create a path to save the Excel file on the desktop
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
excel_file_path = os.path.join(desktop_path, 'sensor_data.xlsx')

try:
    print("Press Ctrl+C to stop data collection and save to Excel.")
    while True:
        if ser.in_waiting >= 1:
            data = ser.readline().decode().strip()
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            row = [timestamp] + data.split(',')
            ws.append(row)
            print(f"{timestamp}: {data}")

except KeyboardInterrupt:
    pass

# Save the Excel file
wb.save(excel_file_path)
print(f"Data collection stopped. Excel file saved to {excel_file_path}")