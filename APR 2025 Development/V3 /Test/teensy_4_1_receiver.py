"""
Teensy 4.1 LoRa Receiver - Message Receiver
This code allows the Teensy 4.1 to receive text messages from a Teensy 4.0 transmitter
using the RYLR998 LoRa radio module.

Hardware connections:
- RYLR998 LoRa module connected to Serial1 (pins 0/1)
- Optional: OLED display for showing received messages (I2C pins 18/19)
- Optional: LED for indicating message reception (pin 13)

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
LORA_ADDRESS = 2           # Address of this device (Teensy 4.1)
LORA_TRANSMITTER = 1       # Address of transmitter (Teensy 4.0)
LORA_NETWORK_ID = 18       # Network ID (must be same for both devices)
LORA_BAND = 915000000      # Frequency in Hz (915MHz for US)
LORA_PARAMETERS = "9,7,1,12"  # SF=9, BW=125kHz, CR=4/5, Preamble=12
SERIAL_TIMEOUT = 1.0       # Timeout for serial operations

# Initialize UART for LoRa module
uart = busio.UART(board.TX1, board.RX1, baudrate=115200, timeout=SERIAL_TIMEOUT)

# Initialize LED for message reception indication
led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT

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
    text_area = label.Label(terminalio.FONT, text="LoRa Receiver\nInitializing...", color=0xFFFFFF, x=5, y=10)
    splash.append(text_area)
    display.show(splash)
except Exception as e:
    print(f"Display initialization failed: {e}")
    display = None

# Message history
message_history = []
MAX_HISTORY = 10

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
    
    # Check module status
    response = send_at_command("AT+VER")
    if response and "OK" in response:
        print("LoRa module initialized successfully")
        update_display("LoRa Ready", "Waiting for messages")
        return True
    else:
        print("Failed to initialize LoRa module")
        update_display("LoRa Error", "Check connections")
        return False

def send_acknowledgment(destination=LORA_TRANSMITTER):
    """Send an acknowledgment message back to the transmitter"""
    message = "ACK: Message received"
    command = f"AT+SEND={destination},{len(message)},{message}"
    response = send_at_command(command, timeout=3.0)
    
    if response and "+SEND:OK" in response:
        print(f"Acknowledgment sent successfully")
        return True
    else:
        print(f"Failed to send acknowledgment")
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

def display_message_history():
    """Display the message history on the OLED"""
    if display and message_history:
        try:
            splash = displayio.Group()
            
            # Show the last message prominently
            last_message = message_history[-1]
            header = label.Label(terminalio.FONT, text="Last Message:", color=0xFFFFFF, x=5, y=10)
            splash.append(header)
            
            # Truncate message if too long
            msg_text = last_message
            if len(msg_text) > 20:
                msg_text = msg_text[:17] + "..."
                
            message_label = label.Label(terminalio.FONT, text=msg_text, color=0xFFFFFF, x=5, y=25)
            splash.append(message_label)
            
            # Show count of messages
            count_label = label.Label(terminalio.FONT, 
                                     text=f"Total: {len(message_history)} msgs", 
                                     color=0xFFFFFF, x=5, y=45)
            splash.append(count_label)
            
            display.show(splash)
        except Exception as e:
            print(f"Display update failed: {e}")

def check_for_lora_message():
    """Check for incoming LoRa messages"""
    if uart.in_waiting > 0:
        # Read the available data
        data = uart.read(uart.in_waiting).decode(errors='ignore')
        
        # Check if it's a received message
        if "+RCV" in data:
            # Parse the received message
            try:
                # Format: +RCV=<sender>,<length>,<message>,<RSSI>,<SNR>
                parts = data.split("=")[1].split(",")
                sender = int(parts[0])
                length = int(parts[1])
                message = parts[2]
                rssi = parts[3] if len(parts) > 3 else "N/A"
                snr = parts[4] if len(parts) > 4 else "N/A"
                
                print(f"Message from {sender}: {message}")
                print(f"Signal: RSSI={rssi}, SNR={snr}")
                
                # Add to history
                message_history.append(message)
                if len(message_history) > MAX_HISTORY:
                    message_history.pop(0)  # Remove oldest message
                
                # Update display
                update_display(f"From: {sender}", message[:16] + ("..." if len(message) > 16 else ""))
                
                # Flash LED
                led.value = True
                time.sleep(0.1)
                led.value = False
                
                # Send acknowledgment
                send_acknowledgment(sender)
                
                # After a delay, show message history
                time.sleep(2)
                display_message_history()
                
                return True
            except Exception as e:
                print(f"Error parsing message: {e}")
                return False
    
    return False

def read_serial_input():
    """Read input from the USB serial connection"""
    if supervisor.runtime.serial_bytes_available:
        return input().strip()
    return None

# Main initialization
print("Teensy 4.1 LoRa Receiver")
print("------------------------")
update_display("Teensy 4.1", "LoRa Receiver")
time.sleep(1)

if initialize_lora():
    print("Ready to receive messages")
    print("Type 'history' to see message history")
    print("Type 'clear' to clear message history")
    print("Type 'AT+...' to send direct AT commands")
    
    # Main loop
    while True:
        # Check for incoming LoRa messages
        check_for_lora_message()
        
        # Check for serial input
        user_input = read_serial_input()
        if user_input:
            if user_input.lower() == "history":
                # Show message history
                print("\nMessage History:")
                for i, msg in enumerate(message_history):
                    print(f"{i+1}. {msg}")
                print("")
                display_message_history()
            elif user_input.lower() == "clear":
                # Clear message history
                message_history.clear()
                print("Message history cleared")
                update_display("History Cleared", "Waiting for messages")
            elif user_input.startswith("AT+"):
                # Direct AT command
                send_at_command(user_input)
            else:
                # Unknown command
                print(f"Unknown command: {user_input}")
        
        # Small delay to prevent CPU hogging
        time.sleep(0.1)
else:
    print("Failed to initialize. Check connections and try again.")
    while True:
        time.sleep(1)
