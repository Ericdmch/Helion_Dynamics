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
blue_light.value = False  # Start OFF

# UART used to send data out to another device
uart = busio.UART(board.TX, board.RX, baudrate=115200)

# Onboard LED
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT

# GPS state variables
last_gps_update = time.monotonic()
latitude = None
longitude = None

# Initialize variables for blue light timer and altitude
blue_light_timer_start = None
blue_light_state = False  # False = OFF, True = ON
timer_active = False  # Timer is initially not active
ground_altitude = bme680.altitude

# Track the ascent and the maximum altitude reached
max_altitude = 0  # Track the maximum altitude reached
ascending = False  # Keep track of whether we are ascending

previous_relative_altitude = None  # Track previous altitude to check if it's stopped changing

led.value = True
time.sleep(5)
led.value = False

def collect_and_send_data():
    global blue_light_timer_start, blue_light_state, timer_active, max_altitude, ascending, previous_relative_altitude

    try:
        timestamp = round(time.monotonic(), 1)

        # Sensor readings
        temperature = round(bme680.temperature, 1)
        pressure = round(bme680.pressure / 10, 1)  # kPa
        altitude = bme680.altitude
        relative_altitude = round(altitude - ground_altitude, 2)

        accel_x, accel_y, accel_z = mpu.acceleration
        accel_x = round(accel_x, 1)
        accel_y = round(accel_y, 1)
        accel_z = round(accel_z, 1)
    except:
        print(f"\nOS ERROR\n")

    analog_value = analog_pin.value

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

    # Track maximum altitude reached
    if relative_altitude > max_altitude:
        max_altitude = relative_altitude
        ascending = True  # We are ascending as long as altitude is increasing

    # Check if we're descending after reaching max altitude
    if relative_altitude < max_altitude:
        ascending = False

    # Print relative altitude each loop
    print(f"Relative Altitude: {relative_altitude}m")

    # Apply blue light timer logic only if we are ascending and above 180m
    if ascending or relative_altitude > 180:
        # Start timer as soon as we are ascending
        if not timer_active:
            timer_active = True
            blue_light_state = True
            blue_light.value = True  # Turn light ON immediately on ascent
            blue_light_timer_start = time.monotonic()
            print("🔵 Blue light ON (ascending, timer started)")

        # Timer-based blinking logic
        elapsed = time.monotonic() - blue_light_timer_start

        if blue_light_state and elapsed >= 30:
            blue_light_state = False
            blue_light.value = False
            blue_light_timer_start = time.monotonic()
            print("🔵 Blue light OFF (30s passed)")

        elif not blue_light_state and elapsed >= 10:
            blue_light_state = True
            blue_light.value = True
            blue_light_timer_start = time.monotonic()
            print("🔵 Blue light ON (10s passed)")

    # Check if the relative altitude has stopped changing (indicating the rocket stopped falling)
    if previous_relative_altitude is not None and abs(relative_altitude - previous_relative_altitude) < 0.08 and not ascending:
        # If the altitude hasn't changed by more than 1m, turn the light on
        blue_light.value = True
        print("🔵 Blue light ON (altitude stopped changing)")

    else:
        # Control blue light based on altitude (below 180m)
        if not ascending and relative_altitude <= 180:
            # Turn the light off when altitude is between 180m and 5m (as the rocket starts descending)
            if relative_altitude <= 180 and blue_light.value:
                blue_light.value = False
                print("🔵 Blue light OFF (descending, between 180m and 5m)")

    # Store the current relative altitude to track for the next loop
    previous_relative_altitude = relative_altitude

while True:
    collect_and_send_data()

    current_time = time.monotonic()
    if current_time - last_gps_update >= 1.0:
        gps.update()
        if gps.has_fix:
            latitude = gps.latitude
            longitude = gps.longitude
            print(f"📍 GPS Fix: lat={latitude}, lon={longitude}")
        else:
            print("⚠️ No GPS fix")
            latitude = None
            longitude = None
        last_gps_update = current_time

    time.sleep(0.1)# Write your code here :-)
