# SPDX-FileCopyrightText: 2025 xAI
# SPDX-License-Identifier: MIT

import board
import busio
import time
import json

# Initialize UART for DX-LR02 (TX7: pin 28, RX7: pin 29)
lora_uart = busio.UART(board.GP4, board.GP5, baudrate=9600)

# Initialize UART for data input (UART0: GP0 and GP1)
data_uart = busio.UART(board.GP0, board.GP1, baudrate=115200)

def send_at_command(cmd, expected, timeout=2.0):
    """Send AT command and check for expected response."""
    lora_uart.write(cmd + "\r\n")
    response = ""
    start_time = time.monotonic()
    while time.monotonic() - start_time < timeout:
        if lora_uart.in_waiting:
            response += lora_uart.read(lora_uart.in_waiting).decode()
        time.sleep(0.01)
    print(f"Sent: {cmd}")
    print(f"Received: {response.strip()}")
    return expected in response

def configure_lora():
    """Configure DX-LR02 module for larger payloads using Level 6 parameters."""
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

    # Configure LoRa parameters for larger payloads
    if not send_at_command("AT+MODE0", "OK"):  # Transparent mode
        print("Failed to set transparent mode")
        return False
    time.sleep(0.5)

    if not send_at_command("AT+SF8", "OK"):  # Set Spreading Factor to 8 (SF6)
        print("Failed to set Spreading Factor to 8")
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
    print("LoRa configuration failed")
while True:
    try:
        # Check for incoming data
        if data_uart.in_waiting:
            #print("Data available on UART0")
            try:
                # Read a line of data
                data_line = data_uart.readline().decode().strip()
                #print(f"Raw data received: {data_line}")

                # Parse JSON data
                try:
                    data_point = json.loads(data_line)
                    #print(f"Parsed data: {data_point}")
                except Exception as e:
                    #print(f"JSON parsing error: {e}")
                    continue

                # Prepare message as JSON
                message = json.dumps(data_point)
                #print(f"Prepared message: {message}")

                # Send data over LoRa UART
                lora_uart.write(message.encode('utf-8') + b'\n')
                #print(f"Sent to LoRa: {message}")

                # Add small delay between transmissions
                time.sleep(0.05)
            except Exception as e:
                print(f"Error processing data: {e}")

        else:
            #print("No data available on UART0", end='\r')
            #lora_uart.write("NO Data!")
            time.sleep(0.1)
    except Exception as e:
        print(f"General exception in main loop: {e}")
        time.sleep(1)
