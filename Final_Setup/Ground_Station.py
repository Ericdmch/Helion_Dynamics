import board
import busio
import time
import json
import re

# Initialize UART for LoRa module
uart_lora = busio.UART(board.TX1, board.RX1, baudrate=115200)

def send_at_command(command):
    full_command = command + "\r\n"
    uart_lora.write(full_command.encode())
    time.sleep(0.5)
    response = uart_lora.read(256)
    if response:
        return response.decode().strip()
    return None

def configure_lora():
    send_at_command("AT+FACTORY")
    time.sleep(1)
    send_at_command("AT+ADDRESS=2")
    send_at_command("AT+NETWORKID=100")
    send_at_command("AT+MODE=0")
    send_at_command("AT+BAND=915000000")
    send_at_command("AT+PARAMETER=9,7,1,12")

def parse_received_data(response):
    if not response:
        return None

    if "+RCV=" in response:
        try:
            match = re.search(r'\+RCV=(\d+),(\d+),\[(.*?)\],(-?\d+),(\d+)', response)
            if match:
                sender_address, data_length, json_data, rssi, snr = match.groups()
                parsed_data = json.loads(f"[{json_data}]")
                formatted_data = "\n--- Received Data ---\n"
                formatted_data += f"Transmitter Address: {sender_address}\n"
                formatted_data += f"Data Length: {data_length} bytes\n"
                formatted_data += f"RSSI: {rssi} dBm\n"
                formatted_data += f"SNR: {snr} dB\n"
                for i, data_point in enumerate(parsed_data):
                    formatted_data += f"\nData Point {i + 1}:\n"
                    formatted_data += f"Raw Data: {data_point}\n"
                print(formatted_data)
                return parsed_data
            return None
        except:
            return None
    elif "+ERR=4" in response:
        return None
    else:
        return None

configure_lora()

while True:
    response = send_at_command("AT+RECV")
    parse_received_data(response)
    time.sleep(0.5)