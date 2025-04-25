# SPDX-FileCopyrightText: 2025 xAI
# SPDX-License-Identifier: MIT

import board
import busio
import time
import json
import adafruit_ssd1306
import adafruit_gps


def scan_i2c(i2c):
    """Scan I2C bus and return list of detected addresses."""
    try:
        i2c.writeto(0x00, b'')  # Dummy write to trigger scan
    except:
        pass
    devices = []
    for addr in range(8, 128):
        try:
            i2c.writeto(addr, b'')
            devices.append(hex(addr))
        except:
            pass
    return devices


# Initialize I2C buses
# I2C2 for OLED (SCL2: pin 24, SDA2: pin 25)
i2c_oled = busio.I2C(board.SCL2, board.SDA2)
# I2C1 for GPS (SCL1: pin 16, SDA1: pin 17)
i2c_gps = busio.I2C(board.SCL, board.SDA)

# Scan and init OLED
devices = scan_i2c(i2c_oled)
print("OLED I2C devices found:", devices)

display = None
for addr in [0x3C, 0x3D]:
    try:
        display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c_oled, addr=addr)
        display.fill(0)
        display.show()
        print(f"SSD1306 initialized at address 0x{addr:02X}")
        break
    except ValueError as e:
        print(f"No SSD1306 at address 0x{addr:02X}: {e}")

if display is None:
    print("SSD1306 initialization failed: No I2C device found")
    def display_message(display, message, clear=True):
        print(f"OLED Message: {message}")
else:
    def display_message(display, message, clear=True):
        try:
            if clear:
                display.fill(0)
            lines = []
            current_line = ""
            for word in message.split():
                if len(current_line) + len(word) + 1 <= 21:
                    current_line += word + " "
                else:
                    lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                lines.append(current_line.strip())
            for i, line in enumerate(lines[:8]):
                display.text(line, 0, i * 8, 1)
            display.show()
            time.sleep(0.01)
        except Exception as e:
            print(f"OLED update error: {e}")

    display_message(display, "Initializing OLED...")
    time.sleep(1)
    display_message(display, "OLED OK")
    time.sleep(1)

# Initialize UART for LoRa (DX-LR02)
lora_uart = busio.UART(board.TX7, board.RX7, baudrate=9600)

# Initialize GPS on I2C1
display_message(display, "Initializing GPS...")
try:
    gps = adafruit_gps.GPS_GtopI2C(i2c_gps, debug=True)
    # Enable RMC and GGA sentences
    gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
    gps.send_command(b"PMTK220,1000")  # 1 Hz update rate
    display_message(display, "GPS OK")
    time.sleep(1)
except Exception as e:
    display_message(display, "GPS Init Failed")
    print(f"GPS initialization failed: {e}")
    gps = None
    time.sleep(5)


def send_at_command(cmd, expected, timeout=2.0):
    lora_uart.write(cmd + b"\r\n")
    response = ""
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        if lora_uart.in_waiting:
            try:
                response += lora_uart.read(lora_uart.in_waiting).decode()
            except Exception as e:
                display_message(display, "LoRa UART Error")
                print(f"UART decode error: {e}")
                return False
        time.sleep(0.01)
    print(f"Sent: {cmd}")
    print(f"Received: {response.strip()}")
    return expected in response


def configure_lora():
    display_message(display, "Configuring LoRa...")
    time.sleep(2)
    # Enter AT mode
    for attempt in range(3):
        if send_at_command(b"+++", "Entry AT", timeout=4.0):
            display_message(display, "LoRa AT Mode OK")
            break
        display_message(display, f"LoRa AT Retry {attempt+1}/3")
        time.sleep(1)
    else:
        display_message(display, "LoRa AT Failed")
        return False
    time.sleep(0.5)
    # Basic test
    if not send_at_command(b"AT", "OK", timeout=4.0):
        display_message(display, "LoRa AT Failed")
        return False
    time.sleep(0.5)
    # Mode, SF, channel, reset
    for cmd, expect in [(b"AT+MODE0","OK"), (b"AT+SF6","OK"), (b"AT+CHANNEL82","OK"), (b"AT+RESET","OK")]:
        if not send_at_command(cmd, expect):
            display_message(display, f"LoRa {cmd.decode()} Failed")
            return False
        time.sleep(0.5)
    # Verify config
    send_at_command(b"+++", "Entry AT", timeout=2.0)
    time.sleep(0.5)
    if not send_at_command(b"AT+HELP","LoRa Parameter"):
        display_message(display, "LoRa Config Failed")
        return False
    send_at_command(b"+++","Exit AT")
    display_message(display, "LoRa OK")
    return True


def get_gps_data(timeout=10.0):
    if gps is None:
        display_message(display, "GPS Not Init")
        return None
    # Try up to 3 attempts
    for attempt in range(1, 4):
        display_message(display, f"GPS Searching... ({attempt}/3)")
        print(f"GPS attempt {attempt}/3")
        start = time.monotonic()
        while time.monotonic() - start < timeout:
            gps.update()
            # Uncomment to debug NMEA sentences
            # if gps.nmea_sentence:
            #     print(f"NMEA: {gps.nmea_sentence}")
            if gps.has_fix and gps.latitude and gps.longitude:
                display_message(display, "GPS Fix OK")
                print(f"GPS fix acquired on attempt {attempt}")
                return {
                    "latitude": gps.latitude,
                    "longitude": gps.longitude,
                    "fix_quality": gps.fix_quality
                }
            time.sleep(0.1)
    # After 3 unsuccessful attempts
    display_message(display, f"No GPS Fix after 3 tries")
    print(f"No GPS fix after 3 attempts")
    return {
        "latitude": None,
        "longitude": None,
        "fix_quality": 0
    }

# Configure LoRa
if not configure_lora():
    display_message(display, "LoRa Config Failed")
    time.sleep(2)

# Main loop
last_gps = 0
gps_interval = 5.0
gps_data = None

while True:
    # LoRa receive
    if lora_uart.in_waiting:
        raw = lora_uart.readline().decode().strip()
        if raw:
            try:
                data = json.loads(raw)
                print(f"LoRa data: {data}")
                if display:
                    display.fill(0)
                    display.text(f"Temp: {data[1]:.1f}C", 0, 0, 1)
                    display.text(f"Press: {data[2]:.3f}kPa", 0, 8, 1)
                    display.text(f"Acc: {data[3]:.1f},{data[4]:.1f}", 0, 16, 1)
                    display.text(f"AccZ: {data[5]:.1f}", 0, 24, 1)
                    if gps_data and gps_data['latitude']:
                        display.text(f"Lat:{gps_data['latitude']:.4f}", 0, 32, 1)
                        display.text(f"Lon:{gps_data['longitude']:.4f}", 0, 40, 1)
                    display.show()
                    time.sleep(0.01)
                # Log
                ts = time.monotonic()
                print(f"[{ts:.3f}] Temp={data[1]}C Press={data[2]}kPa Acc={data[3:]}")
            except json.JSONDecodeError:
                display_message(display, "Invalid JSON")
                print("Invalid JSON format")
    # Periodic GPS
    if time.monotonic() - last_gps >= gps_interval:
        gps_data = get_gps_data()
        last_gps = time.monotonic()
    time.sleep(0.1)
