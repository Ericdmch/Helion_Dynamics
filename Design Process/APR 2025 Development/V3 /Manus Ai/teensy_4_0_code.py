"""
Teensy 4.0 CircuitPython Code
- Collects data from BME680, MPU6050, GPS, photodiode
- Displays information on OLED
- Transmits data to Teensy 4.1 via RYLR998 LoRa radio
"""
import time
import board
import busio
import analogio
import displayio
import adafruit_bme680
import adafruit_mpu6050
import adafruit_gps
import adafruit_displayio_ssd1306
from adafruit_display_text import label
import terminalio
import supervisor

# Configuration constants
LORA_ADDRESS = 1           # Address of this device
LORA_DESTINATION = 2       # Address of Teensy 4.1
LORA_NETWORK_ID = 18       # Network ID (must be same for both devices)
LORA_BAND = 915000000      # Frequency in Hz (915MHz for US)
LORA_PARAMETERS = "9,7,1,12"  # SF=9, BW=125kHz, CR=4/5, Preamble=12
TRANSMISSION_INTERVAL = 10  # Send data every 10 seconds

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize UART for LoRa radio
uart = busio.UART(board.TX2, board.RX2, baudrate=115200)

# Initialize UART for GPS (using I2C GPS, but keeping code for reference)
# gps_uart = busio.UART(board.TX1, board.RX1, baudrate=9600)

# Initialize analog input for photodiode
photodiode = analogio.AnalogIn(board.A0)  # Adjust pin as needed

# Initialize sensors
try:
    bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)
    bme680.sea_level_pressure = 1013.25  # Set to your local pressure for altitude calculation
    print("BME680 initialized")
except Exception as e:
    print(f"BME680 initialization failed: {e}")
    bme680 = None

try:
    mpu = adafruit_mpu6050.MPU6050(i2c)
    print("MPU6050 initialized")
except Exception as e:
    print(f"MPU6050 initialization failed: {e}")
    mpu = None

try:
    gps = adafruit_gps.GPS_GtopI2C(i2c)
    # Turn on the basic GGA and RMC info
    gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
    # Set update rate to once a second (1Hz)
    gps.send_command(b'PMTK220,1000')
    print("GPS initialized")
except Exception as e:
    print(f"GPS initialization failed: {e}")
    gps = None

# Initialize OLED display
try:
    displayio.release_displays()
    display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)  # Adjust address if needed
    display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)
    print("OLED display initialized")
except Exception as e:
    print(f"OLED display initialization failed: {e}")
    display = None

# Function to initialize LoRa module
def init_lora():
    print("Initializing LoRa module...")
    time.sleep(1)  # Give the module time to power up
    
    # Send AT command and wait for response
    def send_at_command(command, wait_time=1):
        print(f"Sending: {command}")
        uart.write(f"{command}\r\n".encode())
        time.sleep(wait_time)
        response = b""
        while uart.in_waiting:
            response += uart.read(uart.in_waiting)
        response_str = response.decode('utf-8', 'ignore').strip()
        print(f"Response: {response_str}")
        return response_str
    
    # Test AT command
    response = send_at_command("AT")
    if "+OK" not in response:
        print("LoRa module not responding")
        return False
    
    # Configure LoRa module
    send_at_command(f"AT+ADDRESS={LORA_ADDRESS}")
    send_at_command(f"AT+NETWORKID={LORA_NETWORK_ID}")
    send_at_command(f"AT+BAND={LORA_BAND}")
    send_at_command(f"AT+PARAMETER={LORA_PARAMETERS}")
    
    print("LoRa module initialized")
    return True

# Function to read sensor data
def read_sensors():
    data = {}
    
    # Read BME680 data
    if bme680:
        try:
            data["temperature"] = bme680.temperature
            data["humidity"] = bme680.relative_humidity
            data["pressure"] = bme680.pressure
            data["gas"] = bme680.gas
            data["altitude"] = bme680.altitude
        except Exception as e:
            print(f"Error reading BME680: {e}")
    
    # Read MPU6050 data
    if mpu:
        try:
            data["acceleration"] = mpu.acceleration
            data["gyro"] = mpu.gyro
            data["temperature_mpu"] = mpu.temperature
        except Exception as e:
            print(f"Error reading MPU6050: {e}")
    
    # Read GPS data
    if gps:
        try:
            gps.update()
            data["gps_fix"] = gps.has_fix
            if gps.has_fix:
                data["latitude"] = gps.latitude
                data["longitude"] = gps.longitude
                data["altitude_gps"] = gps.altitude_m
                data["speed"] = gps.speed_knots
                data["satellites"] = gps.satellites
            else:
                data["gps_status"] = "No fix"
        except Exception as e:
            print(f"Error reading GPS: {e}")
    
    # Read photodiode data
    try:
        data["light"] = photodiode.value
    except Exception as e:
        print(f"Error reading photodiode: {e}")
    
    # Add timestamp
    data["timestamp"] = time.monotonic()
    
    return data

# Function to format data for transmission
def format_data(data):
    # Create a compact string representation of the data
    # Format: temp,hum,press,gas,alt,ax,ay,az,gx,gy,gz,lat,lon,light
    formatted = ""
    
    # BME680 data
    formatted += f"{data.get('temperature', 0):.2f},"
    formatted += f"{data.get('humidity', 0):.2f},"
    formatted += f"{data.get('pressure', 0):.2f},"
    formatted += f"{data.get('gas', 0):.2f},"
    formatted += f"{data.get('altitude', 0):.2f},"
    
    # MPU6050 data
    accel = data.get('acceleration', (0, 0, 0))
    gyro = data.get('gyro', (0, 0, 0))
    formatted += f"{accel[0]:.2f},{accel[1]:.2f},{accel[2]:.2f},"
    formatted += f"{gyro[0]:.2f},{gyro[1]:.2f},{gyro[2]:.2f},"
    
    # GPS data
    formatted += f"{data.get('latitude', 0):.6f},"
    formatted += f"{data.get('longitude', 0):.6f},"
    
    # Photodiode data
    formatted += f"{data.get('light', 0)}"
    
    return formatted

# Function to send data via LoRa
def send_data(data_str):
    command = f"AT+SEND={LORA_DESTINATION},{len(data_str)},{data_str}"
    print(f"Sending data: {command}")
    uart.write(f"{command}\r\n".encode())
    time.sleep(1)  # Wait for transmission
    
    # Read response
    response = b""
    while uart.in_waiting:
        response += uart.read(uart.in_waiting)
    response_str = response.decode('utf-8', 'ignore').strip()
    print(f"Response: {response_str}")
    
    return "+OK" in response_str

# Function to update OLED display
def update_display(data):
    if not display:
        return
    
    # Create a display group
    splash = displayio.Group()
    
    # Add text labels
    text_area = label.Label(terminalio.FONT, text="Teensy 4.0 Sensor Hub", x=5, y=5)
    splash.append(text_area)
    
    # Display BME680 data
    if "temperature" in data:
        text = f"T: {data['temperature']:.1f}C H: {data['humidity']:.1f}%"
        text_area = label.Label(terminalio.FONT, text=text, x=5, y=20)
        splash.append(text_area)
    
    # Display GPS data
    if "gps_fix" in data and data["gps_fix"]:
        text = f"GPS: {data['latitude']:.4f}, {data['longitude']:.4f}"
        text_area = label.Label(terminalio.FONT, text=text, x=5, y=35)
        splash.append(text_area)
    else:
        text_area = label.Label(terminalio.FONT, text="GPS: No Fix", x=5, y=35)
        splash.append(text_area)
    
    # Display light level
    if "light" in data:
        # Convert raw ADC value to percentage
        light_percent = (data["light"] / 65535) * 100
        text = f"Light: {light_percent:.1f}%"
        text_area = label.Label(terminalio.FONT, text=text, x=5, y=50)
        splash.append(text_area)
    
    # Show the group on the display
    display.show(splash)

# Main function
def main():
    print("Teensy 4.0 Sensor Hub Starting...")
    
    # Initialize LoRa module
    if not init_lora():
        print("Failed to initialize LoRa module. Check connections.")
        return
    
    last_transmission_time = 0
    
    while True:
        try:
            # Read sensor data
            data = read_sensors()
            
            # Update display
            update_display(data)
            
            # Check if it's time to transmit
            current_time = time.monotonic()
            if current_time - last_transmission_time >= TRANSMISSION_INTERVAL:
                # Format and send data
                formatted_data = format_data(data)
                if send_data(formatted_data):
                    print("Data sent successfully")
                else:
                    print("Failed to send data")
                
                last_transmission_time = current_time
            
            # Small delay to prevent tight loop
            time.sleep(1)
            
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(5)  # Longer delay on error

# Run the main function
if __name__ == "__main__":
    # Wait a bit for USB serial to be ready
    time.sleep(1)
    main()
