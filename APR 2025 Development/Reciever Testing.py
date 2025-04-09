import board
import busio
import time

# Initialize UART on Pins 0 (RX) and 1 (TX)
uart = busio.UART(board.TX1, board.RX1, baudrate=115200)

# Function to send AT commands
def send_at_command(command):
    uart.write((command + "\r\n").encode())
    time.sleep(0.1)  # Wait for response
    response = uart.read(32)  # Read up to 32 bytes
    if response:
        print("Response:", response.decode().strip())

# Configure RYLR988 (Receiver Address: 2, Network ID: 100)
send_at_command("AT+ADDRESS=2")  # Set receiver address
send_at_command("AT+NETWORKID=100")  # Set network ID
send_at_command("AT+MODE=0")  # Set to normal mode

# Main loop to receive messages
print("Waiting for messages...")
while True:
    if uart.in_waiting > 0:  # Check if data is available
        data = uart.read(uart.in_waiting)  # Read all available data
        if data:
            try:
                message = data.decode().strip()
                if message.startswith("+RCV"):
                    # Example: +RCV=<sender_address>,<length>,<data>,<RSSI>,<SNR>
                    parts = message.split(",", 4)
                    received_data = parts[3]  # Extract the message data
                    print(f"Received: {received_data}")
            except UnicodeError:
                print("Error decoding message")
    time.sleep(0.1)  # Small delay to avoid busy-waiting
