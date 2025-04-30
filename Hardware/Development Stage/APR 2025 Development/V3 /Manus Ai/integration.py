"""
Integration script for Teensy 4.0 and 4.1 LoRa communication system
- Updates the main code files to use the LoRaProtocol class
- Demonstrates how to integrate the protocol into the existing code
"""
import os
import sys

def update_teensy_40_code():
    """Update the Teensy 4.0 code to use the LoRaProtocol class"""
    
    # Import section to add
    import_section = """
# Import LoRaProtocol class
try:
    from lora_protocol import LoRaProtocol
    print("LoRaProtocol imported")
except ImportError:
    print("LoRaProtocol import failed, copy lora_protocol.py to the device")
    
"""
    
    # Replace init_lora function with new implementation
    new_init_lora = """
# Function to initialize LoRa module
def init_lora():
    print("Initializing LoRa module...")
    
    try:
        # Create LoRaProtocol instance
        global lora_protocol
        lora_protocol = LoRaProtocol(uart, LORA_ADDRESS, LORA_DESTINATION, debug=True)
        
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
"""
    
    # Replace send_data function with new implementation
    new_send_data = """
# Function to send data via LoRa
def send_data(data_str):
    try:
        # Use the protocol to send data with acknowledgment
        success = lora_protocol.send_packet(data_str, with_ack=True)
        if success:
            print("Data sent successfully")
        else:
            print("Failed to send data")
        return success
    except Exception as e:
        print(f"Error sending data: {e}")
        return False
"""
    
    # Read the original file
    with open('/home/ubuntu/teensy_project/code/teensy_4_0_code.py', 'r') as f:
        content = f.read()
    
    # Insert import section after existing imports
    import_end = content.find('# Configuration constants')
    if import_end != -1:
        content = content[:import_end] + import_section + content[import_end:]
    
    # Replace init_lora function
    init_lora_start = content.find('# Function to initialize LoRa module')
    init_lora_end = content.find('# Function to read sensor data')
    if init_lora_start != -1 and init_lora_end != -1:
        content = content[:init_lora_start] + new_init_lora + content[init_lora_end:]
    
    # Replace send_data function
    send_data_start = content.find('# Function to send data via LoRa')
    send_data_end = content.find('# Function to update OLED display')
    if send_data_start != -1 and send_data_end != -1:
        content = content[:send_data_start] + new_send_data + content[send_data_end:]
    
    # Write the updated file
    with open('/home/ubuntu/teensy_project/code/teensy_4_0_code_integrated.py', 'w') as f:
        f.write(content)
    
    print("Teensy 4.0 code updated with LoRaProtocol integration")

def update_teensy_41_code():
    """Update the Teensy 4.1 code to use the LoRaProtocol class"""
    
    # Import section to add
    import_section = """
# Import LoRaProtocol class
try:
    from lora_protocol import LoRaProtocol
    print("LoRaProtocol imported")
except ImportError:
    print("LoRaProtocol import failed, copy lora_protocol.py to the device")
    
"""
    
    # Replace init_lora function with new implementation
    new_init_lora = """
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
"""
    
    # Replace check_lora_data function with new implementation
    new_check_lora_data = """
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
"""
    
    # Read the original file
    with open('/home/ubuntu/teensy_project/code/teensy_4_1_code.py', 'r') as f:
        content = f.read()
    
    # Insert import section after existing imports
    import_end = content.find('# Configuration constants')
    if import_end != -1:
        content = content[:import_end] + import_section + content[import_end:]
    
    # Replace init_lora function
    init_lora_start = content.find('# Function to initialize LoRa module')
    init_lora_end = content.find('# Function to read local sensor data')
    if init_lora_start != -1 and init_lora_end != -1:
        content = content[:init_lora_start] + new_init_lora + content[init_lora_end:]
    
    # Replace check_lora_data function
    check_lora_start = content.find('# Function to check for and parse received LoRa data')
    check_lora_end = content.find('# Function to send combined data to computer via USB serial')
    if check_lora_start != -1 and check_lora_end != -1:
        content = content[:check_lora_start] + new_check_lora_data + content[check_lora_end:]
    
    # Write the updated file
    with open('/home/ubuntu/teensy_project/code/teensy_4_1_code_integrated.py', 'w') as f:
        f.write(content)
    
    print("Teensy 4.1 code updated with LoRaProtocol integration")

def create_readme():
    """Create a README file for the project"""
    readme_content = """# Teensy 4.0/4.1 LoRa Sensor System

## Overview
This project implements a sensor data collection and transmission system using two Teensy microcontrollers:
- **Teensy 4.0**: Collects data from multiple sensors and transmits it via LoRa
- **Teensy 4.1**: Receives data from Teensy 4.0, collects additional sensor data, and forwards everything to a computer

## Hardware Requirements

### Teensy 4.0 Components
- Teensy 4.0 microcontroller
- BME680 environmental sensor (I2C)
- MPU6050 accelerometer/gyroscope (I2C)
- GPS module (I2C)
- 0.96 inch OLED display (I2C)
- Photodiode module (analog)
- RYLR998 LoRa radio module (UART)

### Teensy 4.1 Components
- Teensy 4.1 microcontroller
- BME680 environmental sensor (I2C)
- GPS module (UART)
- RYLR998 LoRa radio module (UART)

## Software Requirements
- CircuitPython 9.2.7 or later installed on both Teensy boards
- Python 3.6+ on the computer for data logging
- Required Python packages: pyserial, pandas, openpyxl

## File Structure
- `teensy_4_0_code.py`: CircuitPython code for Teensy 4.0
- `teensy_4_1_code.py`: CircuitPython code for Teensy 4.1
- `lora_protocol.py`: LoRa communication protocol implementation
- `data_logger.py`: Python script for logging data to Excel
- `troubleshooting_guide.md`: Comprehensive troubleshooting guide
- `teensy_4_0_code_integrated.py`: Teensy 4.0 code with LoRaProtocol integration
- `teensy_4_1_code_integrated.py`: Teensy 4.1 code with LoRaProtocol integration

## Installation Instructions

### Setting up the Teensy Boards
1. Install CircuitPython on both Teensy boards:
   - Download the .HEX file from https://circuitpython.org/board/teensy40/ (for Teensy 4.0)
   - Download the .HEX file from https://circuitpython.org/board/teensy41/ (for Teensy 4.1)
   - Use Teensy Loader to flash the .HEX files to the respective boards

2. Install required CircuitPython libraries:
   - Download the Adafruit CircuitPython bundle
   - Copy the following libraries to the lib folder on each Teensy:
     - adafruit_bme680.mpy
     - adafruit_mpu6050.mpy
     - adafruit_gps.mpy
     - adafruit_displayio_ssd1306.mpy
     - adafruit_display_text

3. Copy the code files to the Teensy boards:
   - Copy `teensy_4_0_code.py` (or `teensy_4_0_code_integrated.py`) and `lora_protocol.py` to Teensy 4.0
   - Rename the main code file to `code.py`
   - Copy `teensy_4_1_code.py` (or `teensy_4_1_code_integrated.py`) and `lora_protocol.py` to Teensy 4.1
   - Rename the main code file to `code.py`

### Setting up the Data Logger
1. Install required Python packages on your computer:
   ```
   pip install pyserial pandas openpyxl
   ```

2. Run the data logger script:
   ```
   python data_logger.py --port COM3 --output sensor_data.xlsx
   ```
   Replace `COM3` with the appropriate serial port for your Teensy 4.1.

## Usage
1. Power on both Teensy boards
2. The Teensy 4.0 will collect sensor data and display it on the OLED screen
3. Data will be transmitted from Teensy 4.0 to Teensy 4.1 via LoRa
4. Teensy 4.1 will receive the data, add its own sensor readings, and send everything to the computer
5. The data logger script will save the data to an Excel file

## Troubleshooting
See the `troubleshooting_guide.md` file for detailed troubleshooting information.

## Configuration
- LoRa settings can be adjusted in the configuration constants section of each code file
- Sensor polling intervals can be modified as needed
- Data logger settings can be adjusted using command-line arguments

## License
This project is open source and available under the MIT License.
"""
    
    with open('/home/ubuntu/teensy_project/README.md', 'w') as f:
        f.write(readme_content)
    
    print("README.md created")

def main():
    """Main function to update code files and create README"""
    try:
        update_teensy_40_code()
        update_teensy_41_code()
        create_readme()
        print("All files updated successfully")
    except Exception as e:
        print(f"Error updating files: {e}")

if __name__ == "__main__":
    main()
