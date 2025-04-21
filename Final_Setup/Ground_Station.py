# SPDX-FileCopyrightText: 2025 xAI
# SPDX-License-Identifier: MIT

import board
import busio
import time

# Initialize UART for DX-LR02 (TX7: pin 28, RX7: pin 29)
uart = busio.UART(board.TX7, board.RX7, baudrate=9600)

def send_at_command(cmd, expected, timeout=2.0):
    """Send AT command and check for expected response."""
    uart.write(cmd + "\r\n")
    response = ""
    start_time = time.monotonic()
    while time.monotonic() - start_time < timeout:
        if uart.in_waiting:
            try:
                response += uart.read(uart.in_waiting).decode()
            except:
                print("unicode err")
        time.sleep(0.01)
    print(f"Sent: {cmd}")
    print(f"Received: {response.strip()}")
    return expected in response, response.strip()

def get_rssi():
    """Query RSSI by entering AT command mode."""
    # Enter AT mode
    success, _ = send_at_command("+++", "Entry AT", timeout=4.0)
    if not success:
        print("Failed to enter AT mode for RSSI")
        return None
    time.sleep(0.5)
    # Query RSSI (hypothetical command; confirm with DX-SMART)
    success, response = send_at_command("AT+RSSI", "RSSI", timeout=2.0)
    if success:
        # Parse RSSI (e.g., "RSSI=-65" or similar)
        try:
            rssi = response.split("=")[1].strip()
            return rssi
        except (IndexError, ValueError):
            print("Failed to parse RSSI response")
            return None
    else:
        print("AT+RSSI command failed")
    # Exit AT mode
    send_at_command("+++", "Exit AT", timeout=2.0)
    time.sleep(0.5)
    return None

def configure_lora():
    """Configure DX-LR02 module."""
    # Retry entering AT mode
    for attempt in range(3):
        if send_at_command("+++", "Entry AT", timeout=4.0)[0]:
            print("Entered AT mode")
            break
        print(f"Retry {attempt + 1}/3: Failed to enter AT mode")
        time.sleep(1)
    else:
        print("Failed to enter AT mode after retries")
        return False
    time.sleep(2)  # Wait for module to stabilize
    # Test baud rate and wake module
    print("Testing module communication...")
    if send_at_command("AT", "OK", timeout=4.0)[0]:
        print("Module responded to AT command")
    else:
        print("Module did not respond to AT command. Check baud rate or wiring.")
    time.sleep(0.5)

    time.sleep(0.5)
    if not send_at_command("AT+MODE0", "OK")[0]:
        print("Failed to set transparent mode")
    time.sleep(0.5)
    if not send_at_command("AT+LEVEL4", "OK")[0]:
        print("Failed to set level 4")
    time.sleep(0.5)
    if not send_at_command("AT+CHANNEL82", "OK")[0]:
        print("Failed to set channel 82")
    time.sleep(0.5)
    if not send_at_command("AT+RESET", "OK")[0]:
        print("Failed to reset")
    time.sleep(2)  # Wait for restart
    if not send_at_command("+++", "Entry AT", timeout=2.0)[0]:
        print("Failed to re-enter AT mode for HELP")
    time.sleep(0.5)
    if not send_at_command("AT+HELP", "LoRa Parameter")[0]:
        print("Failed to get configuration info")
    time.sleep(0.5)

# Configure LoRa module
if not configure_lora():
    print("LoRa configuration failed, continuing anyway")

last_rssi_time = 0
rssi_interval = 10  # Query RSSI every 10 seconds

import time
import json
import board
import busio

# Initialize UART
uart = busio.UART(board.TX, board.RX, baudrate=115200)

while True:
    # Check for received data
    if uart.in_waiting:
        try:
            data = uart.readline().decode().strip()
            print(f"Raw data received: {data}")

            # Parse JSON data
            try:
                data_point = json.loads(data)
                if isinstance(data_point, list) and len(data_point) == 9:
                    timestamp, temperature, pressure, accel_x, accel_y, accel_z, latitude, longitude, analog_value = data_point
                    print(f"Received data - Timestamp: {timestamp}, Temperature: {temperature}, Pressure: {pressure}, Accel X: {accel_x}, Accel Y: {accel_y}, Accel Z: {accel_z}, Latitude: {latitude}, Longitude: {longitude}, Analog Value: {analog_value}")
                else:
                    print("Invalid data format or length")
            except json.JSONDecodeError:
                print("Invalid JSON data")
        except UnicodeDecodeError:
            print("Unicode decoding error")
        except Exception as e:
            print(f"An error occurred: {e}")
    time.sleep(0.01)  # Small delay to prevent excessive CPU usage

    # Periodically query RSSI
    current_time = time.monotonic()
    if current_time - last_rssi_time >= rssi_interval:
        rssi = get_rssi()
        if rssi is not None:
            print(f"RSSI: {rssi} dBm")
        last_rssi_time = current_time

    # No sleep to maximize UART polling
