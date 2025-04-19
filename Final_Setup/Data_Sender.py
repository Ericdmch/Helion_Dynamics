import time
import board
import busio
import json

# Initialize UART for Teensy (GP0: TX, GP1: RX)
teensy_uart = busio.UART(board.GP0, board.GP1, baudrate=115200)

# Initialize UART for LoRa module (GP4: TX1, GP5: RX1)
lora_uart = busio.UART(board.GP4, board.GP5, baudrate=115200)

current_line = []  # Buffer for incoming data from Teensy
data_buffer = []   # Buffer to store received packets

def read_teensy_data():
    global current_line
    data_received = False
    message = None
    while teensy_uart.in_waiting > 0:
        byte = teensy_uart.read(1)
        if byte == b'\n':  # End of a line
            if current_line:
                try:
                    message = b''.join(current_line).decode('utf-8').strip()
                    #print(f"Received from Teensy: {message}")
                    data_received = True
                except UnicodeError as e:
                    print(f"Decoding error: {e}")
                finally:
                    current_line = []
        else:
            current_line.append(byte)
    return data_received, message

def send_lora_command(command):
    full_command = command + "\r\n"
    lora_uart.write(full_command.encode())
    print(f"Sent LoRa command: {command}")
    response = ""
    start_time = time.monotonic()
    while "OK" not in response and time.monotonic() - start_time < 2:
        time.sleep(0.1)
        while lora_uart.in_waiting > 0:
            response += lora_uart.read(lora_uart.in_waiting).decode()
    if response:
        print(f"LoRa response: {response.strip()}")
        return response.strip()
    else:
        print("No response from LoRa.")
        return None

def configure_lora():
    print("Configuring LoRa module...")
    send_lora_command("AT+FACTORY")  # Reset to defaults
    time.sleep(1)
    send_lora_command("AT+ADDRESS=1")    # Sender address
    send_lora_command("AT+NETWORKID=100") # Network ID
    send_lora_command("AT+MODE=0")       # Transceiver mode
    send_lora_command("AT+BAND=915000000") # Frequency (915MHz)
    send_lora_command("AT+PARAMETER=9,7,1,12") # RF parameters
    print("LoRa configured.")

configure_lora()
print("Waiting for data from Teensy...")

while True:
    data_received, message = read_teensy_data()
    if data_received:
        try:
            # Parse the received message as JSON (if needed)
            # message_data = json.loads(message)

            # Add the received packet to the buffer
            data_buffer.append(message)
            #print(f"Added packet to buffer. Buffer size: {len(data_buffer)}")

            # Check if we have at least two packets to send
            if len(data_buffer) >= 2:
                # Combine the first two packets into one
                combined_data = data_buffer[:2]
                combined_json = json.dumps(combined_data)

                # Truncate if the combined data exceeds LoRa payload limit (240 bytes)
                max_payload = 240
                if len(combined_json) > max_payload:
                    combined_json = combined_json[:max_payload]
                    print(f"Warning: Payload truncated to {max_payload} bytes")

                # Send the combined data via LoRa
                data_length = len(combined_json)
                send_command = f"AT+SEND=2,{data_length},{combined_json}"
                send_lora_command(send_command)
                #print(f"Sent combined data: {combined_json}")

                # Remove the sent packets from the buffer
                data_buffer = data_buffer[2:]

        except Exception as e:
            print(f"Error processing data: {e}")
    time.sleep(0.1)
