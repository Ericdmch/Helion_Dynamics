import time
import board
import busio
import json
import digitalio

# Initialize the onboard LED
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# Initialize UART for Teensy (GP0: TX, GP1: RX)
teensy_uart = busio.UART(board.GP0, board.GP1, baudrate=115200)

# Initialize UART for DX-LR02 radio (GP4: TX, GP5: RX)
radio_uart = busio.UART(board.GP4, board.GP5, baudrate=9600)

current_line = []
data_buffer = []
packet_count = 0
BATCH_SIZE = 2  # Number of packets to send in each batch

# AT command sending function
def send_at_command(cmd, expected, timeout=2.0):
    try:
        radio_uart.write(cmd + "\r\n")
        response = ""
        start_time = time.monotonic()
        while time.monotonic() - start_time < timeout:
            if radio_uart.in_waiting:
                response += radio_uart.read(radio_uart.in_waiting).decode()
            time.sleep(0.05)
        print(f"Sent: {cmd}")
        print(f"Received: {response.strip()}")
        return expected in response, response.strip()
    except Exception as e:
        print(f"Error sending AT command: {e}")
        return False, ""

# Configure LoRa module
def configure_lora():
    try:
        for attempt in range(3):
            if send_at_command("+++", "Entry AT", timeout=4.0)[0]:
                print("Entered AT mode")
                led.value = True
                time.sleep(0.1)  # Keep LED on for 0.1 seconds
                led.value = False  # Turn off the LED
                break
            print(f"Retry {attempt + 1}/3: Failed to enter AT mode")
            time.sleep(1)
        else:
            print("Failed to enter AT mode after retries")
            return False
        time.sleep(2)  # Wait for module to stabilize
        # Test baud rate and wake module
        print("Testing module communication...")
        if send_at_command("AT", "OK", timeout=4.0)[0]:
            print("Module responded to AT command")
        else:
            print("Module did not respond to AT command. Check baud rate or wiring.")

        if not send_at_command("AT+MODE0", "OK")[0]:
            print("Failed to set transparent mode")
        if not send_at_command("AT+LEVEL4", "OK")[0]:
            print("Failed to set level 4")
        if not send_at_command("AT+CHANNEL82", "OK")[0]:
            print("Failed to set channel 82")
        if not send_at_command("AT+RESET", "OK")[0]:
            print("Failed to reset")
        time.sleep(2)  # Wait for restart
        if not send_at_command("+++", "Entry AT", timeout=2.0)[0]:
            print("Failed to re-enter AT mode for HELP")
        if not send_at_command("AT+HELP", "LoRa Parameter")[0]:
            print("Failed to get configuration info")
        led.value = True
        time.sleep(3)  # Keep LED on for 3 seconds
        led.value = False  # Turn off the LED
        return True
    except Exception as e:
        print(f"Error configuring LoRa: {e}")
        return False

# Read data from Teensy
def read_teensy_data():
    global current_line, packet_count
    data_received = False
    try:
        start_time = time.monotonic()
        while time.monotonic() - start_time < 0.1:
            if teensy_uart.in_waiting > 0:
                byte = teensy_uart.read(1)

                if byte == b'\n':
                    if current_line:
                        try:
                            message = b''.join(current_line).decode('utf-8').strip()
                            try:
                                parsed_data = json.loads(message)
                            except:
                                current_line = []
                                continue

                            if isinstance(parsed_data, list) and len(parsed_data) >= 9:
                                data_buffer.append(parsed_data)
                                packet_count += 1
                                data_received = True
                            else:
                                print(f"Invalid packet format: {parsed_data}")

                        except:
                            print("Error discarding")
                            current_line = []
                else:
                    current_line.append(byte)
        return data_received
    except Exception as e:
        print(f"Error reading Teensy data: {e}")
        return False

# Send data via LoRa in batches
def send_radio_data():
    global data_buffer
    try:
        if len(data_buffer) < BATCH_SIZE:
            return False  # Not enough data to form a batch

        batch = data_buffer[:BATCH_SIZE]
        data_buffer = data_buffer[BATCH_SIZE:]  # Remove the sent packets from the buffer

        json_data = json.dumps(batch)
        try:
            radio_uart.write(json_data.encode() + b'\n')
        except:
            print("send failed")
        print(f"Sent to radio: {json_data}")
        # Turn on the LED
        led.value = True
        time.sleep(0.1)  # Keep LED on for 0.1 seconds
        led.value = False  # Turn off the LED
        return True
    except Exception as e:
        print(f"Error sending radio data: {e}")
        return False

# Main function
def main():
    print("Configuring LoRa module...")
    try:
        if configure_lora():
            print("LoRa module configured successfully")
        else:
            print("LoRa module configuration failed")
            return  # Exit if configuration fails

        print("Waiting for data from Teensy...")

        while True:
            try:
                read_teensy_data()
                # Check if there are enough packets to form a batch and send them
                while len(data_buffer) >= BATCH_SIZE:
                    send_radio_data()
                time.sleep(0.1)
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("Program terminated by user")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
