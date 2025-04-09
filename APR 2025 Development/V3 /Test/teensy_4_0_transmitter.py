"""
Teensy 4.0 LoRa Transmitter - Message Sender
This code allows the Teensy 4.0 to send text messages to a Teensy 4.1 receiver
using the RYLR998 LoRa radio module.

Hardware connections:
- RYLR998 LoRa module connected to Serial1 (pins 0/1)
- Optional: OLED display for status (I2C pins 18/19)
- Optional: Button for sending messages (pin 2)

Author: Manus
Date: April 9, 2025
"""

import time
import board
import busio
import digitalio
import supervisor
import displayio
import terminalio
from adafruit_display_text import label
import adafruit_displayio_ssd1306

# Configuration constants
LORA_ADDRESS = 1           # Address of this device (Teensy 4.0)
LORA_DESTINATION = 2       # Address of receiver (Teensy 4.1)
LORA_NETWORK_ID = 18       # Network ID (must be same for both devices)
LORA_BAND = 915000000      # Frequency in Hz (915MHz for US)
LORA_PARAMETERS = "9,7,1,12"  # SF=9, BW=125kHz, CR=4/5, Preamble=12
LORA_POWER = 15            # Transmit power (0-15, with 15 being highest)
SERIAL_TIMEOUT = 1.0       # Timeout for serial operations

# Initialize UART for LoRa module
uart = busio.UART(board.TX1, board.RX1, baudrate=115200, timeout=SERIAL_TIMEOUT)

# Initialize button for sending predefined messages
button = digitalio.DigitalInOut(board.D2)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP
button_state = False
last_button_state = False

# Initialize I2C for OLED display
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize OLED display (if connected)
display = None
try:
    displayio.release_displays()
    display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
    display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)
    
    # Create a display group and add a text label
    splash = displayio.Group()
    text_area = label.Label(terminalio.FONT, text="LoRa Transmitter\nInitializing...", color=0xFFFFFF, x=5, y=10)
    splash.append(text_area)
    display.show(splash)
except Exception as e:
    print(f"Display initialization failed: {e}")
    display = None

# Predefined messages to send when button is pressed
messages = [
    "Hello from Teensy 4.0!",
    "This is a test message",
    "LoRa communication test",
    "How's the signal strength?",
    "Message received? Please confirm."
]
message_index = 0

def send_at_command(command, wait_for_response=True, timeout=1.0):
    """Send AT command to LoRa module and wait for response"""
    print(f"Sending: {command}")
    uart.write(f"{command}\r\n".encode())
    
    if not wait_for_response:
        return None
    
    # Wait for response with timeout
    response = ""
    start_time = time.monotonic()
    while time.monotonic() - start_time < timeout:
        if uart.in_waiting > 0:
            byte = uart.read(1)
            if byte:
                response += byte.decode(errors='ignore')
                if response.endswith("\r\n"):
                    response = response.strip()
                    print(f"Received: {response}")
                    return response
        time.sleep(0.01)
    
    print("Response timeout")
    return None

def initialize_lora():
    """Initialize the LoRa module with configuration settings"""
    # Reset the module to factory settings
    send_at_command("AT+FACTORY")
    time.sleep(1)
    
    # Configure LoRa parameters
    send_at_command(f"AT+ADDRESS={LORA_ADDRESS}")
    send_at_command(f"AT+NETWORKID={LORA_NETWORK_ID}")
    send_at_command(f"AT+BAND={LORA_BAND}")
    send_at_command(f"AT+PARAMETER={LORA_PARAMETERS}")
    send_at_command(f"AT+CRFOP={LORA_POWER}")
    
    # Check module status
    response = send_at_command("AT+VER")
    if response and "OK" in response:
        print("LoRa module initialized successfully")
        update_display("LoRa Ready", "Press button to send")
        return True
    else:
        print("Failed to initialize LoRa module")
        update_display("LoRa Error", "Check connections")
        return False

def send_message(message, destination=LORA_DESTINATION):
    """Send a message to the specified destination"""
    command = f"AT+SEND={destination},{len(message)},{message}"
    response = send_at_command(command, timeout=3.0)
    
    if response and "+SEND:OK" in response:
        print(f"Message sent successfully: {message}")
        update_display("Message Sent", message[:16] + ("..." if len(message) > 16 else ""))
        return True
    else:
        print(f"Failed to send message: {message}")
        update_display("Send Failed", "Check LoRa module")
        return False

def update_display(line1, line2=""):
    """Update the OLED display with status information"""
    if display:
        try:
            splash = displayio.Group()
            text_area = label.Label(terminalio.FONT, text=f"{line1}\n{line2}", color=0xFFFFFF, x=5, y=10)
            splash.append(text_area)
            display.show(splash)
        except Exception as e:
            print(f"Display update failed: {e}")

def read_serial_input():
    """Read input from the USB serial connection"""
    if supervisor.runtime.serial_bytes_available:
        return input().strip()
    return None

# Main initialization
print("Teensy 4.0 LoRa Transmitter")
print("---------------------------")
update_display("Teensy 4.0", "LoRa Transmitter")
time.sleep(1)

if initialize_lora():
    print("Ready to send messages")
    print("Press the button to send a predefined message")
    print("Or type a message and press Enter to send")
    
    # Main loop
    while True:
        # Check button for sending predefined messages
        button_state = not button.value  # Button is active LOW
        if button_state and not last_button_state:
            # Button was just pressed
            message = messages[message_index]
            message_index = (message_index + 1) % len(messages)
            send_message(message)
            time.sleep(0.5)  # Debounce
        last_button_state = button_state
        
        # Check for serial input
        user_input = read_serial_input()
        if user_input:
            if user_input.startswith("AT+"):
                # Direct AT command
                send_at_command(user_input)
            else:
                # Regular message
                send_message(user_input)
        
        # Small delay to prevent CPU hogging
        time.sleep(0.1)
else:
    print("Failed to initialize. Check connections and try again.")
    while True:
        time.sleep(1)
