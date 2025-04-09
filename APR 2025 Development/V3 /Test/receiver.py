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

# Test basic AT command
send_at_command("AT")

# Reset to factory defaults (optional)
send_at_command("AT+FACTORY")
time.sleep(1)  # Wait for reset

# Configure RYLR998 (Receiver Address: 2, Network ID: 100)
send_at_command("AT+ADDRESS=2")
send_at_command("AT+NETWORKID=100")
send_at_command("AT+MODE=0")  # Set to transceiver mode

# Main loop
print("Waiting for messages...")
while True:
    # Read incoming data
    if uart.in_waiting > 0:
        data = uart.read(uart.in_waiting).decode().strip()
        print("Received data:", data)

        # Check if the data is a received LoRa message
        if data.startswith("+RCV="):
            # Parse the received data
            parts = data.split(",")
            if len(parts) >= 4:
                address = parts[0].split("=")[1]  # Sender address
                length = parts[1]  # Data length
                message = ",".join(parts[2:-2])  # Extract the message
                rssi = parts[-2]  # Signal strength
                snr = parts[-1]  # Signal-to-noise ratio

                print(f"Received message from address {address}:")
                print(f"Message: {message}")
                print(f"Length: {length} bytes")
                print(f"RSSI: {rssi} dBm")
                print(f"SNR: {snr}")
                print("-" * 30)
