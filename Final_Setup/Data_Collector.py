import time
import json
import board
import busio
import adafruit_bme680
import adafruit_gps
import adafruit_mpu6050
import analogio
from digitalio import DigitalInOut, Direction

# Initialize high-speed I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize sensors
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)
bme680.sea_level_pressure = 101325

gps = adafruit_gps.GPS_GtopI2C(i2c, debug=False)
gps.send_command(b'PMTK314,0,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
gps.send_command(b'PMTK220,1000')

mpu = adafruit_mpu6050.MPU6050(i2c)
mpu.accelerometer_range = adafruit_mpu6050.Range.RANGE_2_G
mpu.gyro_range = adafruit_mpu6050.GyroRange.RANGE_250_DPS


analog_pin = analogio.AnalogIn(board.A1)

blue_light = DigitalInOut(board.D21)
blue_light.direction = Direction.OUTPUT
blue_light.value = True  # Light starts on

# UART used to send data out to another device
uart = busio.UART(board.TX, board.RX, baudrate=115200)

# Onboard LED
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT

# GPS state variables
last_gps_update = time.monotonic()
latitude = None
longitude = None

led.value = True
time.sleep(5)
ground_altitude = bme680.altitude
led.value = False

def collect_and_send_data():
    try:
        timestamp = round(time.monotonic(), 1)

        # Sensor readings
        temperature = round(bme680.temperature, 3)
        pressure = round(bme680.pressure / 10, 3)  # kPa
        altitude = bme680.altitude
        relative_altitude = round(altitude - ground_altitude, 1)

        accel_x, accel_y, accel_z = mpu.acceleration
        accel_x = round(accel_x, 1)
        accel_y = round(accel_y, 1)
        accel_z = round(accel_z, 1)
    except:
        print(f"\nOS ERROR\n")


    analog_value = analog_pin.value-60000

    data_point = [
        timestamp,
        temperature,
        pressure,
        accel_x,
        accel_y,
        accel_z,
        latitude,
        longitude,
        analog_value,
        relative_altitude
    ]

    json_data = json.dumps(data_point)

    # Send via UART
    uart.write(json_data.encode('utf-8') + b'\n')

    # Print to serial monitor
    print(f"Data @ {timestamp}s: {json_data}")

    # Blink LED to confirm data was sent
    led.value = True
    time.sleep(0.05)
    led.value = False

    # Control blue light based on altitude
    if relative_altitude <= 180 and blue_light.value:
        blue_light.value = False
        #print("️️Blue light OFF (below 180m)")

    if relative_altitude <= 5 and not blue_light.value:
        blue_light.value = True
        #print("🔵 Blue light ON (below 5m)")

while True:
    collect_and_send_data()

    current_time = time.monotonic()
    if current_time - last_gps_update >= 1.0:
        gps.update()
        if gps.has_fix:
            latitude = gps.latitude
            longitude = gps.longitude
            #print(f"📍 GPS Fix: lat={latitude}, lon={longitude}")
        else:
            #print("⚠️ No GPS fix")
            latitude = None
            longitude = None
        last_gps_update = current_time

    time.sleep(0.1)
