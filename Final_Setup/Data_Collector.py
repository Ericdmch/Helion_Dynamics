import time
import json
import board
import busio
import adafruit_bme680
import adafruit_gps
import adafruit_mpu6050
import analogio

# Initialize I2C for sensors
i2c = board.I2C()

# Initialize BME680
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)
bme680.sea_level_pressure = 101325  # Adjust based on your location

# Initialize GPS
gps = adafruit_gps.GPS_GtopI2C(i2c, debug=False)
gps.send_command(b'PMTK314,0,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
gps.send_command(b'PMTK220,1000')

# Initialize MPU6050
mpu = adafruit_mpu6050.MPU6050(i2c)
mpu.accelerometer_range = adafruit_mpu6050.Range.RANGE_2_G
mpu.gyro_range = adafruit_mpu6050.GyroRange.RANGE_250_DPS

# Initialize analog input on a valid analog pin (e.g., A0)
analog_pin = analogio.AnalogIn(board.A2)

# Initialize UART for communication with Pico
uart = busio.UART(board.TX1, board.RX1, baudrate=115200)

def collect_and_send_data():
    # Get timestamp rounded to the nearest tenth of a second
    timestamp = round(time.monotonic(), 1)

    # Read BME680 data
    temperature = round(bme680.temperature, 1)
    pressure = bme680.pressure/10  # Convert to kiloPascals

    # Read GPS data
    gps.update()
    latitude = None
    longitude = None
    if gps.has_fix:
        latitude = gps.latitude
        longitude = gps.longitude

    # Read MPU6050 data
    accel_x, accel_y, accel_z = mpu.acceleration

    # Read analog data from the specified analog pin
    analog_value = analog_pin.value

    # Create simplified data payload without sensor labels
    data_point = [
        timestamp,
        temperature,
        pressure,
        round(accel_x, 1),
        round(accel_y, 1),
        round(accel_z, 1),
        latitude,
        longitude,
        analog_value
    ]

    # Convert data to JSON and send over serial
    json_data = json.dumps(data_point)
    uart.write(json_data.encode('utf-8') + b'\n')
    print("Sent data:", json_data.encode('utf-8') + b'\n')

while True:
    collect_and_send_data()
    time.sleep(0.3)
