import board
import busio
import time
import json
import re
import digitalio

# Initialize UART for LoRa module
uart_lora = busio.UART(board.TX1, board.RX1, baudrate=115200)

# Initialize the switch
switch = digitalio.DigitalInOut(board.D2)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP  # Use internal pull-up resistor

# Initialize digital pin 3
d3 = digitalio.DigitalInOut(board.D3)
d3.direction = digitalio.Direction.OUTPUT

# Function to send AT commands with debug output
def send_at_command(command):
    full_command = command + "\r\n"
    uart_lora.write(full_command.encode())
    time.sleep(0.5)  # Wait for 0.5 seconds to ensure the module has time to respond
    response = uart_lora.read(256)  # Read up to 256 bytes
    if response:
        response_str = response.decode().strip()
        print("Response:", response_str)
        return response_str
    else:
        print("No response")
        return None

# Configure LoRa module
def configure_lora():
    send_at_command("AT+FACTORY")  # Reset to factory defaults
    time.sleep(1)
    send_at_command("AT+ADDRESS=2")  # Receiver address
    send_at_command("AT+NETWORKID=100")  # Network ID (must match sender)
    send_at_command("AT+MODE=0")  # Transceiver mode
    send_at_command("AT+BAND=915000000")  # Frequency (adjust as needed)
    send_at_command("AT+PARAMETER=9,7,1,12")  # RF parameters (adjust as needed)

# Parse received data and format for serial output
def parse_received_data(response):
    if not response:
        return None

    # Check if the response contains valid data
    if "+RCV=" in response:
        try:
            # Extract the data part using regex
            match = re.search(r'\+RCV=(\d+),(\d+),\[\[(.*?)\]\],(-?\d+),(\d+)', response)
            if match:
                sender_address, data_length, json_data, rssi, snr = match.groups()

                # Convert the JSON string to a Python object
                parsed_data = json.loads(f"[[{json_data}]]")

                # Print formatted data
                formatted_data = "\n--- Received Data ---\n"
                formatted_data += f"Transmitter Address: {sender_address}\n"
                formatted_data += f"Data Length: {data_length} bytes\n"
                formatted_data += f"RSSI: {rssi} dBm\n"
                formatted_data += f"SNR: {snr} dB\n"

                # Print each data point in the packet
                for i, data_point in enumerate(parsed_data):
                    formatted_data += f"\nData Point {i + 1}:\n"
                    formatted_data += f"Timestamp: {data_point[0]:.2f} seconds\n"

                    # GPS Data
                    gps_data = data_point[1]
                    formatted_data += "\nGPS Data:\n"
                    if len(gps_data) >= 2:
                        formatted_data += f"Latitude: {gps_data[0]}\n"
                        formatted_data += f"Longitude: {gps_data[1]}\n"
                    else:
                        formatted_data += "No GPS data available.\n"

                    # BME680 Data
                    bme680_data = data_point[2]
                    formatted_data += "\nBME680 Data:\n"
                    if len(bme680_data) >= 2:
                        formatted_data += f"Pressure: {bme680_data[0]:.0f} Pa\n"
                        formatted_data += f"Temperature: {bme680_data[1]:.1f} °C\n"
                    else:
                        formatted_data += "No BME680 data available.\n"

                # Send formatted data via serial
                uart_lora.write(formatted_data.encode())
                print(formatted_data)

                return parsed_data
            else:
                print("Received data format is incomplete or invalid:", response)
                return None
        except ValueError as e:
            print("Error decoding JSON data:", e)
            return None
        except Exception as e:
            print("Unexpected error:", e)
            return None
    elif "+ERR=4" in response:
        # Ignore "Unknown command" error
        return None
    else:
        print("Unexpected response:", response)
        return None

# Main setup
configure_lora()
print("Receiver configured. Waiting for switch to be connected...")

# Main loop
while True:
    try:
        # Check if the switch is connected (LOW)
        if not switch.value:
            print("Switch connected. Starting data reception...")
            d3.value = False  # Set D3 to LOW
            # Check for incoming data
            response = send_at_command("AT+RECV")
            parse_received_data(response)
        else:
            print("Switch disconnected. Stopping data reception.")
            d3.value = True  # Set D3 to HIGH

    except Exception as e:
        print("Error in receiver loop:", e)

    time.sleep(0.5)  # Check for data every 0.5 seconds
