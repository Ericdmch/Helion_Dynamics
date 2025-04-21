import time  # Import the time module for time-related functions
import board  # Import the board module for hardware definitions
import busio  # Import the busio module for UART communication
import json  # Import the json module for JSON data handling
import digitalio  # Import the digitalio module for digital I/O operations

# Initialize UART for Teensy (GP0: TX, GP1: RX)
teensy_uart = busio.UART(board.GP0, board.GP1, baudrate=115200)

# Initialize UART for LoRa module (GP4: TX1, GP5: RX1)
lora_uart = busio.UART(board.GP4, board.GP5, baudrate=115200)

# Initialize onboard LED
led = digitalio.DigitalInOut(board.LED)  # Create a digital I/O object for the LED
led.direction = digitalio.Direction.OUTPUT  # Set the LED pin as an output

current_line = []  # Buffer to store incoming data from Teensy line by line
data_buffer = []   # Buffer to store received data packets
packet_count = 0   # Counter to track the number of packets received

def read_teensy_data():
    global current_line, packet_count  # Declare global variables to modify them inside the function
    data_received = False  # Flag to indicate if data was received

    # Read all available data with a timeout of 100ms
    start_time = time.monotonic()  # Record the start time
    while time.monotonic() - start_time < 0.1:  # Continue reading until timeout
        if teensy_uart.in_waiting > 0:  # Check if there is data waiting in the UART buffer
            byte = teensy_uart.read(1)  # Read one byte from the UART

            if byte == b'\n':  # Check if the end of a line is reached
                if current_line:  # If there is data in the current line buffer
                    try:
                        message = b''.join(current_line).decode('utf-8').strip()  # Convert bytes to string and remove whitespace
                        # Parse the message as JSON
                        try:
                            parsed_data = json.loads(message)  # Attempt to parse the JSON data
                        except:
                            print("exception Called!")  # Print an error message if parsing fails
                            current_line = []  # Clear the current line buffer
                            continue  # Skip to the next iteration

                        # Validate the packet structure
                        if isinstance(parsed_data, list) and len(parsed_data) >= 9:  # Check if parsed data is a list with at least 9 elements
                            data_buffer.append(parsed_data)  # Add the valid packet to the data buffer
                            packet_count += 1  # Increment the packet count
                            data_received = True  # Set the data received flag to True
                        else:
                            print(f"Invalid packet format, discarding: {parsed_data}")  # Print an error message for invalid packets

                    except UnicodeError as e:  # Catch Unicode errors during decoding
                        print(f"JSON Error: {e}, discarding packet: {message}")  # Print the error message
                        current_line = []  # Clear the current line buffer
                    finally:
                        current_line = []  # Clear the current line buffer after processing
            else:
                current_line.append(byte)  # Add the received byte to the current line buffer

    return data_received  # Return whether data was received

def send_lora_command(command, retries=0, max_retries=3):
    full_command = command + "\r\n"  # Format the command with a newline character
    lora_uart.write(full_command.encode())  # Send the command over UART
    print(f"Sent LoRa command: {command}")  # Print the sent command

    response = ""  # Initialize the response variable
    start_time = time.monotonic()  # Record the start time
    while "OK" not in response and time.monotonic() - start_time < 2:  # Wait for a response with a timeout of 2 seconds
        time.sleep(0.1)  # Short delay to avoid busy waiting
        while lora_uart.in_waiting > 0:  # Read all available data from the UART buffer
            response += lora_uart.read(lora_uart.in_waiting).decode()  # Decode and append the received data to the response

    if response:  # If a response was received
        print(f"LoRa response: {response.strip()}")  # Print the response
        # Blink the onboard LED when receiving "+OK"
        if "+OK" in response:  # Check if the response contains "+OK"
            led.value = True  # Turn on the LED
            time.sleep(0.1)  # Keep the LED on for a short duration
            led.value = False  # Turn off the LED
        # If the command is AT+FACTORY and ERR is in response, retry
        elif command == "AT+FACTORY" and "ERR" in response:  # Check if the command is AT+FACTORY and response contains ERR
            retries += 1  # Increment the retry count
            if retries <= max_retries:  # Check if retry count is within the limit
                print(f"Command '{command}' failed. Retrying ({retries}/{max_retries})...")  # Print retry message
                return send_lora_command(command, retries, max_retries)  # Retry the command
            else:
                print(f"Command '{command}' failed after {max_retries} retries.")  # Print failure message after max retries
        return response.strip()  # Return the stripped response
    else:
        print("No response from LoRa.")  # Print message if no response was received
        return None  # Return None for no response

def configure_lora():
    print("Configuring LoRa module...")  # Print configuration start message
    send_lora_command("AT+FACTORY")  # Send AT+FACTORY command to reset to defaults
    time.sleep(1)  # Wait for 1 second after factory reset
    send_lora_command("AT+ADDRESS=1")    # Set the LoRa module address to 1
    send_lora_command("AT+NETWORKID=100") # Set the network ID to 100
    send_lora_command("AT+MODE=0")       # Set the mode to transceiver (0)
    send_lora_command("AT+BAND=915000000") # Set the frequency band to 915MHz
    send_lora_command("AT+PARAMETER=9,7,1,12") # Set RF parameters
    print("LoRa configured.")  # Print configuration completion message

configure_lora()  # Call the function to configure the LoRa module
print("Waiting for data from Teensy...")  # Print a message indicating readiness to receive data

while True:  # Main loop to continuously run the program
    data_received = read_teensy_data()  # Read data from Teensy and check if data was received

    if data_received:  # If data was received
        try:
            # Check if there are at least two packets in the buffer to combine and send
            if len(data_buffer) >= 2:
                combined_data = data_buffer[:2]  # Take the first two packets from the buffer
                combined_json = json.dumps(combined_data)  # Convert the combined data to a JSON string

                print(f"\nCombined JSON: {combined_json}")  # Print the combined JSON data

                # Truncate the JSON string if it exceeds the LoRa payload limit of 240 bytes
                max_payload = 240
                if len(combined_json) > max_payload:
                    combined_json = combined_json[:max_payload]  # Truncate the JSON string
                    print(f"Warning: Payload truncated to {max_payload} bytes")  # Print a warning message

                # Send the combined JSON data via LoRa
                data_length = len(combined_json)  # Get the length of the JSON data
                send_command = f"AT+SEND=2,{data_length},{combined_json}"  # Format the send command
                send_lora_command(send_command)  # Send the command to LoRa

                # Remove the sent packets from the data buffer
                data_buffer = data_buffer[2:]
                #print(f"Buffer after send: {data_buffer}")  # Debug line to print buffer after sending

        except Exception as e:  # Catch any exceptions during data processing
            print(f"Error processing data: {e}")  # Print the error message

    # Add status information
    #print(f"Status: Packets received={packet_count}, Buffer size={len(data_buffer)}", end='\r')  # Debug line to print status

    time.sleep(0.1)  # Short delay to avoid busy waiting and allow other processes to run
