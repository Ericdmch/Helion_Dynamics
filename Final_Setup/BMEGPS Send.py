import board
import busio
import time
import json
import adafruit_bme680
import adafruit_gps
import asyncio

# Initialize UART for LoRa module
uart = busio.UART(board.TX1, board.RX1, baudrate=115200)

# Initialize I2C for BME680 and GPS
i2c = board.I2C()
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug=False)
gps = adafruit_gps.GPS_GtopI2C(i2c, debug=False)

# Set sea level pressure (adjust based on your location)
bme680.sea_level_pressure = 101325

# Temperature offset (calibrate as needed)
temperature_offset = -5

# Function to send AT commands with debug output
def send_at_command(command):
    full_command = command + "\r\n"
    uart.write(full_command.encode())
    print(f"Sent command: {command}")

    # Wait for response
    response = ""
    start_time = time.monotonic()
    while "OK" not in response and time.monotonic() - start_time < 2:  # Wait up to 2 seconds
        time.sleep(0.1)
        while uart.in_waiting > 0:
            response += uart.read(uart.in_waiting).decode()

    if response:
        print(f"Response: {response.strip()}")
        return response.strip()
    else:
        print("No response received.")
        return None

# Configure LoRa module
def configure_lora():
    print("Configuring LoRa module...")
    send_at_command("AT+FACTORY")  # Reset to factory defaults
    time.sleep(3)
    send_at_command("AT+ADDRESS=1")  # Sender address
    send_at_command("AT+NETWORKID=100")  # Network ID
    send_at_command("AT+MODE=0")  # Transceiver mode
    send_at_command("AT+BAND=915000000")  # Frequency (adjust as needed)
    send_at_command("AT+PARAMETER=9,7,1,12")  # RF parameters (adjust as needed)
    print("LoRa module configured.")

# Configure GPS
def configure_gps():
    print("Configuring GPS module...")
    # Turn on only the GPRMC and GPGGA sentences
    gps.send_command(b'PMTK314,0,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
    # Set update rate to once per second
    gps.send_command(b'PMTK220,1000')
    print("GPS module configured.")

# Main setup
configure_lora()
configure_gps()
print("Sender configured. Starting data collection...")

# Buffer to store data points
data_buffer = []
start_time = time.monotonic()

# Asynchronous function to collect data
async def collect_data():
    global start_time
    start_time = time.monotonic()
    while True:
        current_time = time.monotonic() - start_time

        # Read BME680 sensor data
        temperature = bme680.temperature + temperature_offset
        pressure = bme680.pressure*1000

        # Read GPS data
        gps.update()
        gps_data = [None, None]  # [latitude, longitude]
        if gps.has_fix:
            gps_data = [
                round(gps.latitude, 6),
                round(gps.longitude, 6)
            ]

        # Create compact data payload
        data_point = [
            round(current_time,1),  # Timestamp
            gps_data,      # GPS data [lat, lon]
            [
                int("{:.0f}".format(pressure)),
                round(temperature, 1)
            ]   # BME680 data [pres, temp]
        ]

        # Add data point to buffer
        data_buffer.append(data_point)
        print(f"Data point added to buffer. Buffer size: {len(data_buffer)}")

        await asyncio.sleep(0.1)  # Collect data every 0.1 seconds

# Function to find the closest data point to a target timestamp
def find_closest_data_point(buffer, target_timestamp):
    closest_point = None
    min_diff = float('inf')
    for dp in buffer:
        diff = abs(dp[0] - target_timestamp)
        if diff < min_diff:
            min_diff = diff
            closest_point = dp
    return closest_point

# Asynchronous function to send packets
async def send_packets():
    global start_time
    start_time = time.monotonic()
    await asyncio.sleep(5)  # Wait for 5 seconds before starting to send

    last_packet_time = start_time
    while True:
        # Calculate the target timestamps for this packet
        target_timestamps = [last_packet_time + i * 0.5 for i in range(4)]
        last_packet_time += 2  # Update for next packet

        packet_data = []
        for ts in target_timestamps:
            print(f"Finding closest data point to {ts} seconds...")
            closest_point = find_closest_data_point(data_buffer, ts)
            if closest_point:
                packet_data.append(closest_point)
                # Remove the sent data point from the buffer
                data_buffer.remove(closest_point)
            else:
                print(f"No data point found near {ts} seconds.")

        if packet_data:
            # Convert packet data to JSON string
            json_data = json.dumps(packet_data)

            # Check payload size
            if len(json_data) > 240:
                print("Warning: Payload size exceeds 240 bytes. Truncating data.")
                json_data = json_data[:240]

            # Send data via LoRa
            print("Sending packet...")
            command = f"AT+SEND=2,{len(json_data)},{json_data}"
            send_at_command(command)

            # Print sent data for debugging
            print(f"Sent data: {json_data}")
        else:
            print("No data points found for this packet.")

        await asyncio.sleep(2)  # Send packets every 2 seconds

# Main loop
async def main():
    await asyncio.gather(collect_data(), send_packets())

# Run the main loop
asyncio.run(main())
