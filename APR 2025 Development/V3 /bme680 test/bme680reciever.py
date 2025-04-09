import board
import busio
import time
import json

# Initialize UART
uart = busio.UART(board.TX1, board.RX1, baudrate=115200)

# Function to send AT commands with debug output
def send_at_command(command):
    full_command = command + "\r\n"
    uart.write(full_command.encode())
    time.sleep(0.1)
    response = uart.read(32)
    if response:
        print("Response:", response.decode().strip())
    else:
        print("No response")

# Function to configure the module
def configure_module():
    send_at_command("AT+FACTORY")
    time.sleep(1)
    send_at_command("AT+ADDRESS=2")       # Receiver address
    send_at_command("AT+NETWORKID=100")   # Network ID
    send_at_command("AT+MODE=0")          # Transceiver mode
    send_at_command("AT+BAND=915000000")  # Frequency
    send_at_command("AT+PARAMETER=9,7,1,12")  # RF parameters

# Function to parse received data
def parse_lora_message(data):
    try:
        parts = data.split(",")
        if len(parts) >= 5 and parts[0].startswith("+RCV="):
            address = parts[0].split("=")[1]
            length = parts[1]
            message = ",".join(parts[2:-2])
            rssi = parts[-2]
            snr = parts[-1]

            # Try to parse JSON data
            try:
                sensor_data = json.loads(message)
                return {
                    "address": address,
                    "length": length,
                    "message": message,
                    "rssi": rssi,
                    "snr": snr,
                    "sensor_data": sensor_data
                }
            except json.JSONDecodeError:
                return {
                    "address": address,
                    "length": length,
                    "message": message,
                    "rssi": rssi,
                    "snr": snr,
                    "sensor_data": None
                }
        return None
    except Exception as e:
        print("Error parsing data:", e)
        return None

# Main setup
configure_module()
print("Receiver configured. Waiting for messages...")

# Main loop
while True:
    if uart.in_waiting > 0:
        data = uart.read(uart.in_waiting).decode().strip()
        print("Raw received data:", data)

        parsed_data = parse_lora_message(data)
        if parsed_data and parsed_data["sensor_data"]:
            print("\nParsed Message:")
            print(f"Sender Address: {parsed_data['address']}")
            print(f"Message Length: {parsed_data['length']} bytes")
            print(f"RSSI: {parsed_data['rssi']} dBm")
            print(f"SNR: {parsed_data['snr']}")
            print("\nSensor Data:")
            for key, value in parsed_data["sensor_data"].items():
                print(f"  {key}: {value}")
            print("-" * 30)
        elif parsed_data:
            print("Received non-JSON data.")
        else:
            print("Received data is not a valid LoRa message.")
