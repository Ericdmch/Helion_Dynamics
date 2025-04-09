"""
Teensy 4.1 CircuitPython Code
- Receives data from Teensy 4.0 via RYLR998 LoRa radio
- Collects data from BME680 and GPS
- Forwards all data to computer for Excel logging
"""
import time
import board
import busio
import adafruit_bme680
import adafruit_gps
import supervisor
import json


# Import LoRaProtocol class
try:
    from lora_protocol import LoRaProtocol
    print("LoRaProtocol imported")
except ImportError:
    print("LoRaProtocol import failed, copy lora_protocol.py to the device")
    
# Configuration constants
LORA_ADDRESS = 2           # Address of this device
LORA_SOURCE = 1            # Address of Teensy 4.0
LORA_NETWORK_ID = 18       # Network ID (must be same for both devices)
LORA_BAND = 915000000      # Frequency in Hz (915MHz for US)
LORA_PARAMETERS = "9,7,1,12"  # SF=9, BW=125kHz, CR=4/5, Preamble=12
DATA_CHECK_INTERVAL = 0.5     # Check for new data every 1 second

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize UART for LoRa radio
uart_lora = busio.UART(board.TX2, board.RX2, baudrate=115200)

# Initialize UART for GPS (TX/RX GPS)
uart_gps = busio.UART(board.TX1, board.RX1, baudrate=9600)

# Initialize sensors
try:
    bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)
    bme680.sea_level_pressure = 1013.25  # Set to your local pressure for altitude calculation
    print("BME680 initialized")
except Exception as e:
    print(f"BME680 initialization failed: {e}")
    bme680 = None

try:
    gps = adafruit_gps.GPS(uart_gps, debug=False)
    # Turn on the basic GGA and RMC info
    gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
    # Set update rate to once a second (1Hz)
    gps.send_command(b'PMTK220,1000')
    print("GPS initialized")
except Exception as e:
    print(f"GPS initialization failed: {e}")
    gps = None


# Function to initialize LoRa module
def init_lora():
    print("Initializing LoRa module...")
    
    try:
        # Create LoRaProtocol instance
        global lora_protocol
        lora_protocol = LoRaProtocol(uart_lora, LORA_ADDRESS, LORA_SOURCE, debug=True)
        
        # Initialize the module
        success = lora_protocol.initialize(LORA_NETWORK_ID, LORA_BAND, LORA_PARAMETERS)
        if not success:
            print("Failed to initialize LoRa module")
            return False
        
        print("LoRa module initialized")
        return True
    except Exception as e:
        print(f"Error initializing LoRa: {e}")
        return False
# Function to read local sensor data
def read_local_sensors():
    data = {}
    
    # Read BME680 data
    if bme680:
        try:
            data["t41_temperature"] = bme680.temperature
            data["t41_humidity"] = bme680.relative_humidity
            data["t41_pressure"] = bme680.pressure
            data["t41_gas"] = bme680.gas
            data["t41_altitude"] = bme680.altitude
        except Exception as e:
            print(f"Error reading BME680: {e}")
    
    # Read GPS data
    if gps:
        try:
            gps.update()
            data["t41_gps_fix"] = gps.has_fix
            if gps.has_fix:
                data["t41_latitude"] = gps.latitude
                data["t41_longitude"] = gps.longitude
                data["t41_altitude_gps"] = gps.altitude_m
                data["t41_speed"] = gps.speed_knots
                data["t41_satellites"] = gps.satellites
            else:
                data["t41_gps_status"] = "No fix"
        except Exception as e:
            print(f"Error reading GPS: {e}")
    
    # Add timestamp
    data["t41_timestamp"] = time.monotonic()
    
    return data


# Function to check for and parse received LoRa data
def check_lora_data():
    try:
        # Use the protocol to receive data
        data_str = lora_protocol.receive_packet(timeout=1)
        if not data_str:
            return None
        
        print(f"Received data: {data_str}")
        
        # Parse the data string into values
        values = data_str.split(',')
        
        # Create a dictionary with the received data
        if len(values) >= 14:  # Ensure we have all expected values
            data = {
                "t40_temperature": float(values[0]),
                "t40_humidity": float(values[1]),
                "t40_pressure": float(values[2]),
                "t40_gas": float(values[3]),
                "t40_altitude": float(values[4]),
                "t40_accel_x": float(values[5]),
                "t40_accel_y": float(values[6]),
                "t40_accel_z": float(values[7]),
                "t40_gyro_x": float(values[8]),
                "t40_gyro_y": float(values[9]),
                "t40_gyro_z": float(values[10]),
                "t40_latitude": float(values[11]),
                "t40_longitude": float(values[12]),
                "t40_light": float(values[13]),
                # RSSI and SNR are handled internally by the protocol
            }
            return data
        else:
            print(f"Incomplete data received: {values}")
    except Exception as e:
        print(f"Error parsing received data: {e}")
    
    return None
# Function to send combined data to computer via USB serial
def send_to_computer(data):
    if not data:
        return
    
    try:
        # Convert data to JSON string
        json_data = json.dumps(data)
        
        # Send data over USB serial
        print("DATA_BEGIN")  # Marker for the computer to recognize start of data
        print(json_data)
        print("DATA_END")    # Marker for the computer to recognize end of data
        
    except Exception as e:
        print(f"Error sending data to computer: {e}")

# Main function
def main():
    print("Teensy 4.1 Data Receiver Starting...")
    
    # Initialize LoRa module
    if not init_lora():
        print("Failed to initialize LoRa module. Check connections.")
        return
    
    # Main loop
    while True:
        try:
            # Check for data from Teensy 4.0
            received_data = check_lora_data()
            
            # If we received data, combine with local sensor data and send to computer
            if received_data:
                # Read local sensor data
                local_data = read_local_sensors()
                
                # Combine the data
                combined_data = {**received_data, **local_data}
                
                # Send to computer
                send_to_computer(combined_data)
                print("Combined data sent to computer")
            else:
                # If no data received, still read and send local data periodically
                local_data = read_local_sensors()
                if local_data:
                    send_to_computer(local_data)
            
            # Small delay to prevent tight loop
            time.sleep(DATA_CHECK_INTERVAL)
            
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(5)  # Longer delay on error

# Run the main function
if __name__ == "__main__":
    # Wait a bit for USB serial to be ready
    time.sleep(1)
    main()
