# SPDX-FileCopyrightText: 2025 xAI
# SPDX-License-Identifier: MIT

import board
import busio
import time
import json
import adafruit_ssd1306

# Initialize I2C for SSD1306 (SCL2: pin 24, SDA2: pin 25)
displayi2c = busio.I2C(board.SCL2, board.SDA2)

# Initialize SSD1306 (128x64, I2C address 0x3C)
try:
    display = adafruit_ssd1306.SSD1306_I2C(128, 64, displayi2c, addr=0x3C)
    display.fill(0)
    display.show()
except ValueError as e:
    print("SSD1306 initialization failed:", e)
    while True:
        pass

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
                print("uni errr")
        time.sleep(0.01)
    print(f"Sent: {cmd}")
    print(f"Received: {response.strip()}")
    return expected in response

def configure_lora():
    """Configure DX-LR02 module."""
    time.sleep(2)  # Wait for module to stabilize

    # Retry entering AT mode
    for attempt in range(3):
        if send_at_command("+++", "Entry AT", timeout=4.0):
            print("Entered AT mode")
            break
        print(f"Retry {attempt + 1}/3: Failed to enter AT mode")
        time.sleep(1)
    else:
        print("Failed to enter AT mode after retries")
        return False
    time.sleep(0.5)

    print("Testing module communication...")
    if send_at_command("AT", "OK", timeout=4.0):
        print("Module responded to AT command")
    else:
        print("Module did not respond to AT command. Check baud rate or wiring.")
        return False
    time.sleep(0.5)

    # Configure LoRa parameters to match sender
    if not send_at_command("AT+MODE0", "OK"):  # Transparent mode
        print("Failed to set transparent mode")
        return False
    time.sleep(0.5)

    if not send_at_command("AT+SF6", "OK"):  # Set Spreading Factor to 6 (SF6)
        print("Failed to set Spreading Factor to 6")
        return False
    time.sleep(0.5)

    if not send_at_command("AT+CHANNEL82", "OK"):  # Set channel
        print("Failed to set channel 82")
        return False
    time.sleep(0.5)

    if not send_at_command("AT+RESET", "OK"):  # Reset module
        print("Failed to reset")
        return False
    time.sleep(2)  # Wait for restart

    if not send_at_command("+++", "Entry AT", timeout=2.0):  # Re-enter AT mode
        print("Failed to re-enter AT mode for HELP")
        return False
    time.sleep(0.5)

    if not send_at_command("AT+HELP", "LoRa Parameter"):  # Verify configuration
        print("Failed to get configuration info")
        return False
    time.sleep(0.5)

    if not send_at_command("+++", "Exit AT"):  # Exit AT mode
        print("Failed to exit AT mode")
        return False
    return True

# Configure LoRa module
if not configure_lora():
    print("LoRa configuration failed, continuing anyway")

while True:
    if uart.in_waiting:
        try:
            # Read data from LoRa UART
            data = uart.readline().decode().strip()
            if data:
                #print(f"Raw data received: {data}")

                # Parse JSON data
                try:
                    data_point = json.loads(data)
                    print(f"Parsed data: {data_point}")

                    # Update OLED display
                    display.fill(0)
                    display.text(f"Temp: {data_point[1]:.1f}°C", 0, 0, 1)
                    display.text(f"Press: {data_point[2]:.3f}kPa", 0, 16, 1)
                    display.text(f"Accel: {data_point[3]:.1f}, {data_point[4]:.1f}, {data_point[5]:.1f}", 0, 32, 1)
                    display.show()

                    # Log data to console
                    timestamp = time.monotonic()
                    print(f"Received ({timestamp:.3f}):")
                    print(f"Timestamp: {data_point[0]}")
                    print(f"Temperature: {data_point[1]}°C")
                    print(f"Pressure: {data_point[2]}kPa")
                    print(f"Acceleration: {data_point[3]}, {data_point[4]}, {data_point[5]}")
                    print(f"Location: {data_point[6]}, {data_point[7]}")
                    print(f"Analog Reading: {data_point[8]}")
                    print("-" * 20)
                except:
                    print("Invalid format")
        except Exception as e:
            print(f"Error processing data: {e}")
    else:
        time.sleep(0.1)  # Short delay to prevent busy waiting
