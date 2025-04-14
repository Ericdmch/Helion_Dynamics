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
        # Check if the data starts with +RCV=
        if data.startswith("+RCV="):
            # Remove the +RCV= prefix
            data = data[5:]

            # Split the remaining data
            parts = data.split(",")
            if len(parts) >= 4:
                address = parts[0]  # Sender address
                length = parts[1]   # Data length
                rssi = parts[-2]    # RSSI
                snr = parts[-1]     # SNR

                # Extract the message content
                message = ",".join(parts[2:-2])

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

# Buffer to accumulate incoming data
data_buffer = ""

# Main loop
while True:
    if uart.in_waiting > 0:
        # Read incoming data
        incoming_data = uart.read(uart.in_waiting).decode(errors="replace").strip()
        data_buffer += incoming_data

        # Process the buffer to find complete messages
        while "+RCV=" in data_buffer:
            # Find the start of a message
            start_idx = data_buffer.find("+RCV=")

            # Find the end of the message (assuming messages are line-based)
            end_idx = data_buffer.find("\n", start_idx)
            if end_idx == -1:
                end_idx = len(data_buffer)

            # Extract the message
            message_str = data_buffer[start_idx:end_idx].strip()

            # Remove the processed message from the buffer
            data_buffer = data_buffer[end_idx:]

            # Parse the message
            parsed_data = parse_lora_message(message_str)
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
