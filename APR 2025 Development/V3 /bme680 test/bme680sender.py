import board
import busio
import time
import json
import adafruit_bme680

# Initialize UART for LoRa module
uart = busio.UART(board.TX1, board.RX1, baudrate=115200)

# Initialize I2C for BME680
i2c = board.I2C()
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug=False)

# Set sea level pressure (adjust based on your location)
bme680.sea_level_pressure = 1013.25

# Temperature offset (calibrate as needed)
temperature_offset = -5

# Function to send AT commands with debug output
def send_at_command(command):
    full_command = command + "\r\n"
    uart.write(full_command.encode())
    time.sleep(0.1)
    response = uart.read(32)
    if response:
        print("Response:", response.decode().strip())
    else:
        print("No response")

# Configure LoRa module
def configure_lora():
    send_at_command("AT+FACTORY")  # Reset to factory defaults
    time.sleep(1)
    send_at_command("AT+ADDRESS=1")  # Sender address
    send_at_command("AT+NETWORKID=100")  # Network ID
    send_at_command("AT+MODE=0")  # Transceiver mode
    send_at_command("AT+BAND=915000000")  # Frequency (adjust as needed)
    send_at_command("AT+PARAMETER=9,7,1,12")  # RF parameters (adjust as needed)

# Main setup
configure_lora()
print("Sender configured. Starting data transmission...")

# Main loop
while True:
    try:
        # Read BME680 sensor data
        temperature = bme680.temperature + temperature_offset
        gas = bme680.gas
        humidity = bme680.relative_humidity
        pressure = bme680.pressure
        altitude = bme680.altitude

        # Create a data payload
        data = {
            "temperature": round(temperature, 1),
            "humidity": round(humidity, 1),
            "pressure": round(pressure, 3),
            "gas": gas,
            "altitude": round(altitude, 2)
        }

        # Convert data to JSON string
        json_data = json.dumps(data)

        # Send data via LoRa
        command = f"AT+SEND=2,{len(json_data)},{json_data}"
        send_at_command(command)

        # Print sent data for debugging
        print(f"Sent data: {json_data}")

    except Exception as e:
        print("Error reading sensor or sending data:", e)

    time.sleep(5)  # Send data every 5 seconds
