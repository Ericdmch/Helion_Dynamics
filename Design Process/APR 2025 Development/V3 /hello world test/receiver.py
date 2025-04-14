import board
import busio
import time

# Initialize UART
uart = busio.UART(board.TX1, board.RX1, baudrate=115200)

# Function to send AT commands with debug output
def send_at_command(command):
    full_command = command + "\r\n"
    print("Sending:", repr(full_command))  # Show exact string with escapes
    uart.write(full_command.encode())
    time.sleep(0.1)
    response = uart.read(32)
    if response:
        print("Response:", response.decode().strip())
    else:
        print("No response")

# Function to configure the module
def configure_module():
    # Reset to factory defaults
    send_at_command("AT+FACTORY")
    time.sleep(1)  # Wait for reset

    # Configure module parameters
    send_at_command("AT+ADDRESS=2")       # Receiver address
    send_at_command("AT+NETWORKID=100")   # Network ID (must match sender)
    send_at_command("AT+MODE=0")          # Transceiver mode
    send_at_command("AT+BAND=915000000")  # Frequency (match sender)
    send_at_command("AT+PARAMETER=9,7,1,12")  # RF parameters (match sender)

# Function to parse received data
def parse_lora_message(data):
    try:
        # Split the received string by commas
        parts = data.split(",")

        # Check if it's a valid LoRa message
        if len(parts) >= 5 and parts[0].startswith("+RCV="):
            # Extract individual components
            address = parts[0].split("=")[1]  # Sender address
            length = parts[1]                 # Data length
            message = ",".join(parts[2:-2])   # Extract the message content
            rssi = parts[-2]                  # Signal strength
            snr = parts[-1]                   # Signal-to-noise ratio

            return {
                "address": address,
                "length": length,
                "message": message,
                "rssi": rssi,
                "snr": snr
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
    # Check if there's incoming data
    if uart.in_waiting > 0:
        # Read all available data
        data = uart.read(uart.in_waiting).decode().strip()
        print("Raw received data:", data)

        # Parse the data
        parsed_data = parse_lora_message(data)

        if parsed_data:
            # Print parsed information
            print("\nParsed Message:")
            print(f"Sender Address: {parsed_data['address']}")
            print(f"Message Length: {parsed_data['length']} bytes")
            print(f"Message Content: {parsed_data['message']}")
            print(f"RSSI: {parsed_data['rssi']} dBm")
            print(f"SNR: {parsed_data['snr']}")
            print("-" * 30)
        else:
            print("Received data is not a valid LoRa message.")
