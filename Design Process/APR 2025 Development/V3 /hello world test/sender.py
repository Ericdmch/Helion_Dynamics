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

# Configure RYLR998 (Sender Address: 1, Network ID: 100)
send_at_command("AT+ADDRESS=1")
send_at_command("AT+NETWORKID=100")
send_at_command("AT+MODE=0")

# Main loop
message_count = 0
while True:
    message = f"Hello from Sender: {message_count}"
    # Fix: Use AT+SEND instead of +SEND
    send_at_command(f"AT+SEND=2,{len(message)},{message}")
    print(f"Intended message: {message}")
    message_count += 1
    time.sleep(1)
