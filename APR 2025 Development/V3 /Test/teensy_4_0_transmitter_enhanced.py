"""
Teensy 4.0 LoRa Transmitter - Enhanced Version with Error Handling
This code allows the Teensy 4.0 to send text messages to a Teensy 4.1 receiver
using the RYLR998 LoRa radio module, with robust error handling and recovery.

Hardware connections:
- RYLR998 LoRa module connected to Serial1 (pins 0/1)
- Optional: OLED display for status (I2C pins 18/19)
- Optional: Button for sending messages (pin 2)
- Optional: Status LED (pin 13)

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
import error_handling

# Configuration constants
LORA_ADDRESS = 1           # Address of this device (Teensy 4.0)
LORA_DESTINATION = 2       # Address of receiver (Teensy 4.1)
LORA_NETWORK_ID = 18       # Network ID (must be same for both devices)
LORA_BAND = 915000000      # Frequency in Hz (915MHz for US)
LORA_PARAMETERS = "9,7,1,12"  # SF=9, BW=125kHz, CR=4/5, Preamble=12
LORA_POWER = 15            # Transmit power (0-15, with 15 being highest)
SERIAL_TIMEOUT = 1.0       # Timeout for serial operations
ACK_TIMEOUT = 5.0          # Timeout for acknowledgment
MAX_RETRIES = 3            # Maximum retries for sending messages

# Initialize UART for LoRa module
uart = busio.UART(board.TX1, board.RX1, baudrate=115200, timeout=SERIAL_TIMEOUT)

# Initialize button for sending predefined messages
button = digitalio.DigitalInOut(board.D2)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP
button_state = False
last_button_state = False

# Initialize status LED
status_led = digitalio.DigitalInOut(board.D13)
status_led.direction = digitalio.Direction.OUTPUT
status_led.value = False

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
    error_handling.track_error("display")
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

# Flag for acknowledgment received
ack_received = False

def blink_led(count=1, duration=0.1):
    """Blink the status LED"""
    for _ in range(count):
        status_led.value = True
        time.sleep(duration)
        status_led.value = False
        time.sleep(duration)

def send_at_command(command, wait_for_response=True, timeout=1.0):
    """Send AT command to LoRa module and wait for response"""
    print(f"Sending: {command}")
    try:
        uart.write(f"{command}\r\n".encode())
    except Exception as e:
        print(f"UART write error: {e}")
        if error_handling.track_error("uart_timeout"):
            error_handling.enter_recovery_mode(uart, update_display)
        return None
    
    if not wait_for_response:
        return None
    
    # Wait for response with timeout
    response = ""
    start_time = time.monotonic()
    while time.monotonic() - start_time < timeout:
        if uart.in_waiting > 0:
            try:
                byte = uart.read(1)
                if byte:
                    response += byte.decode(errors='ignore')
                    if response.endswith("\r\n"):
                        response = response.strip()
                        print(f"Received: {response}")
                        error_handling.record_success("lora_command")
                        error_handling.reset_error_count("uart_timeout")
                        return response
            except Exception as e:
                print(f"UART read error: {e}")
                if error_handling.track_error("uart_timeout"):
                    error_handling.enter_recovery_mode(uart, update_display)
                return None
        time.sleep(0.01)
    
    print("Response timeout")
    error_handling.track_error("uart_timeout")
    return None

def initialize_lora():
    """Initialize the LoRa module with configuration settings"""
    # Reset the module to factory settings
    send_at_command("AT+FACTORY")
    time.sleep(1)
    
    # Configure LoRa parameters
    success = True
    if not send_at_command(f"AT+ADDRESS={LORA_ADDRESS}"):
        success = False
    if not send_at_command(f"AT+NETWORKID={LORA_NETWORK_ID}"):
        success = False
    if not send_at_command(f"AT+BAND={LORA_BAND}"):
        success = False
    if not send_at_command(f"AT+PARAMETER={LORA_PARAMETERS}"):
        success = False
    if not send_at_command(f"AT+CRFOP={LORA_POWER}"):
        success = False
    
    # Check module status
    response = send_at_command("AT+VER")
    if response and "OK" in response and success:
        print("LoRa module initialized successfully")
        update_display("LoRa Ready", "Press button to send")
        error_handling.reset_error_count("lora_init")
        blink_led(3, 0.1)  # 3 quick blinks for success
        return True
    else:
        print("Failed to initialize LoRa module")
        update_display("LoRa Error", "Check connections")
        if error_handling.track_error("lora_init"):
            error_handling.enter_recovery_mode(uart, update_display)
        blink_led(1, 1.0)  # 1 long blink for error
        return False

def send_message(message, destination=LORA_DESTINATION, retries=MAX_RETRIES):
    """Send a message to the specified destination with retries"""
    global ack_received
    
    for attempt in range(retries + 1):
        if attempt > 0:
            print(f"Retry attempt {attempt}/{retries}")
            update_display("Retrying...", f"Attempt {attempt}/{retries}")
            blink_led(2, 0.2)  # 2 medium blinks for retry
        
        # Send the message
        command = f"AT+SEND={destination},{len(message)},{message}"
        response = send_at_command(command, timeout=3.0)
        
        if response and "+SEND:OK" in response:
            print(f"Message sent successfully: {message}")
            update_display("Message Sent", message[:16] + ("..." if len(message) > 16 else ""))
            error_handling.record_success("send")
            error_handling.reset_error_count("send_failure")
            blink_led(1, 0.1)  # 1 quick blink for sent
            
            # Wait for acknowledgment
            ack_received = False
            ack_start_time = time.monotonic()
            update_display("Waiting for ACK", f"Timeout: {ACK_TIMEOUT}s")
            
            while time.monotonic() - ack_start_time < ACK_TIMEOUT:
                check_for_acknowledgment()
                if ack_received:
                    print("Acknowledgment received")
                    update_display("ACK Received", "Message confirmed")
                    error_handling.record_success("receive_ack")
                    error_handling.reset_error_count("no_ack")
                    blink_led(2, 0.1)  # 2 quick blinks for ACK
                    return True
                time.sleep(0.1)
            
            print("No acknowledgment received")
            error_handling.track_error("no_ack")
        else:
            print(f"Failed to send message: {message}")
            update_display("Send Failed", "Retrying...")
            if error_handling.track_error("send_failure"):
                error_handling.enter_recovery_mode(uart, update_display)
                return False
    
    update_display("Send Failed", "Max retries reached")
    blink_led(5, 0.1)  # 5 quick blinks for failure
    return False

def check_for_acknowledgment():
    """Check for acknowledgment message from receiver"""
    global ack_received
    
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
                message = parts[2]
                
                if sender == LORA_DESTINATION and "ACK" in message:
                    ack_received = True
                    return True
            except Exception as e:
                print(f"Error parsing message: {e}")
    
    return False

def update_display(line1, line2=""):
    """Update the OLED display with status information"""
    if display:
        try:
            splash = displayio.Group()
            text_area = label.Label(terminalio.FONT, text=f"{line1}\n{line2}", color=0xFFFFFF, x=5, y=10)
            splash.append(text_area)
            display.show(splash)
            error_handling.reset_error_count("display")
        except Exception as e:
            print(f"Display update failed: {e}")
            error_handling.track_error("display")

def read_serial_input():
    """Read input from the USB serial connection"""
    if supervisor.runtime.serial_bytes_available:
        return input().strip()
    return None

def check_system_health():
    """Periodically check system health"""
    health_status, message = error_handling.check_system_health()
    if not health_status:
        print(f"System health check failed: {message}")
        update_display("System Warning", message)
        blink_led(3, 0.3)  # 3 medium blinks for warning
    return health_status

# Main initialization
print("Teensy 4.0 LoRa Transmitter - Enhanced Version")
print("---------------------------------------------")
update_display("Teensy 4.0", "LoRa Transmitter")
blink_led(1, 0.5)  # 1 medium blink on startup
time.sleep(1)

# Initialize error handling
error_handling.reset_all_error_counts()

# Health check timer
last_health_check = time.monotonic()
HEALTH_CHECK_INTERVAL = 60  # Check system health every 60 seconds

if initialize_lora():
    print("Ready to send messages")
    print("Press the button to send a predefined message")
    print("Or type a message and press Enter to send")
    print("Type 'status' to check system status")
    print("Type 'reset' to reset the system")
    
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
        
        # Check for acknowledgments
        check_for_acknowledgment()
        
        # Check for serial input
        user_input = read_serial_input()
        if user_input:
            if user_input.startswith("AT+"):
                # Direct AT command
                send_at_command(user_input)
            elif user_input.lower() == "status":
                # Check and display system status
                health_status, message = error_handling.check_system_health()
                print(f"System status: {'HEALTHY' if health_status else 'WARNING'}")
                print(f"Message: {message}")
                print("Error counts:")
                for error_type, count in error_handling.error_counts.items():
                    print(f"  {error_type}: {count}/{error_handling.MAX_ERRORS[error_type]}")
                update_display("System Status", "HEALTHY" if health_status else "WARNING")
            elif user_input.lower() == "reset":
                # Manual reset
                print("Manual reset requested")
                update_display("Manual Reset", "Restarting...")
                time.sleep(1)
                supervisor.reload()
            else:
                # Regular message
                send_message(user_input)
        
        # Periodic health check
        if time.monotonic() - last_health_check > HEALTH_CHECK_INTERVAL:
            check_system_health()
            last_health_check = time.monotonic()
        
        # Small delay to prevent CPU hogging
        time.sleep(0.1)
else:
    print("Failed to initialize. Check connections and try again.")
    while True:
        # Blink SOS pattern
        for _ in range(3):  # 3 short blinks (S)
            blink_led(1, 0.2)
            time.sleep(0.2)
        time.sleep(0.4)
        for _ in range(3):  # 3 long blinks (O)
            blink_led(1, 0.6)
            time.sleep(0.2)
        time.sleep(0.4)
        for _ in range(3):  # 3 short blinks (S)
            blink_led(1, 0.2)
            time.sleep(0.2)
        time.sleep(1.0)
