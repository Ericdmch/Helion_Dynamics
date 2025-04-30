import board
import busio
import time
import json
import adafruit_ssd1306
import random

def scan_i2c(i2c):
    try:
        i2c.writeto(0x00, b'')
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

def display_message(display, message, clear=True):
    if display:
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
            display.fill(0)
            display.show()

def send_at_command(cmd, expected, timeout=2.0):
    lora_uart.write(cmd + b"\r\n")
    response = ""
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        if lora_uart.in_waiting:
            try:
                response += lora_uart.read(lora_uart.in_waiting).decode("utf-8", "replace")
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
    if not send_at_command(b"AT", "OK", timeout=4.0):
        display_message(display, "LoRa AT Failed")
        return False
    time.sleep(0.5)
    for cmd, expect in [(b"AT+MODE0", "OK"), (b"AT+SF6", "OK"), (b"AT+CHANNEL82", "OK"), (b"AT+RESET", "OK")]:
        if not send_at_command(cmd, expect):
            display_message(display, f"LoRa {cmd.decode()} Failed")
            return False
        time.sleep(0.5)
    send_at_command(b"+++", "Entry AT", timeout=2.0)
    time.sleep(0.5)
    if not send_at_command(b"AT+HELP", "LoRa Parameter"):
        display_message(display, "LoRa Config Failed")
        return False
    send_at_command(b"+++", "Exit AT")
    display_message(display, "LoRa OK")
    return True

def process_data(raw):
    try:
        data = json.loads(raw)

        if isinstance(data[0], list):  # It's a list of lists
            datasets = data
        else:  # It's a single dataset
            datasets = [data]

        for dataset in datasets:
            if pc_uart:
                pc_uart.write((json.dumps(dataset) + "\n").encode("utf-8"))
                print("sent through uart to computer")

            timestamp = dataset[0]
            temp = dataset[1] - 5.0
            pressure = dataset[2]
            acc_x, acc_y, acc_z = dataset[3], dataset[4], dataset[5]
            lat, lon = dataset[6], dataset[7]
            fluor = dataset[8]
            rel_alt = dataset[9]

            if display:
                display.fill(0)
                display.text(f"Temp: {temp:.1f}C", 0, 0, 1)
                display.text(f"Press: {pressure:.3f}kPa", 0, 8, 1)
                display.text(f"Acc: {acc_x:.1f},{acc_y:.1f},{acc_z:.1f}", 0, 16, 1)
                display.text(f"Lat: {lat:.5f}", 0, 24, 1)
                display.text(f"Lon: {lon:.5f}", 0, 32, 1)
                display.text(f"Fluo: {fluor:.2f}", 0, 40, 1)
                display.text(f"Alt: {rel_alt:.2f}m", 0, 48, 1)
                display.show()
                time.sleep(0.01)

    except Exception as e:
        display_message(display, "Invalid JSON")
        print(f"Invalid JSON format: {e}")

#Debugging
def generate_random_data():
    dataset = [
        round(random.uniform(400, 500), 1),  # timestamp
        round(random.uniform(20, 40), 1),    # temp
        round(random.uniform(90, 105), 1),   # pressure
        round(random.uniform(-10, 10), 1),   # acc_x
        round(random.uniform(-10, 10), 1),   # acc_y
        round(random.uniform(-10, 10), 1),   # acc_z
        round(49.6944 + random.uniform(-0.01, 0.01), 5),  # lat
        round(-112.81 + random.uniform(-0.01, 0.01), 5),  # lon
        random.randint(64000, 66000),         # fluor
        round(random.uniform(-10, 1000), 2)   # rel_alt
    ]
    return [dataset, dataset]

# ---- Main setup ----

i2c_oled = busio.I2C(board.SCL2, board.SDA2)
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

display_message(display, "Initializing OLED...")
time.sleep(1)
display_message(display, "OLED OK")
time.sleep(1)

lora_uart = busio.UART(board.TX7, board.RX7, baudrate=9600)
pc_uart = busio.UART(board.TX, board.RX, baudrate=9600)

if not configure_lora():
    display_message(display, "LoRa Config Failed")
    time.sleep(2)

# ---- Main loop ----

test_mode = False     # manual JSON input
random_mode = False  # random data generator

while True:
    if test_mode:
        raw = input("Enter sample JSON data: ").strip()
        if raw:
            process_data(raw)
    elif random_mode:
        random_data = generate_random_data()
        raw = json.dumps(random_data)
        print("Generated random data:", raw)
        process_data(raw)
        time.sleep(1.0)  # slow down so it's readable
    else:
        if lora_uart.in_waiting:
            try:
                raw = lora_uart.readline().decode("utf-8", "replace").strip()
                print(raw)
            except Exception as e:
                display_message(display, "LoRa Decode Error")
                print(f"LoRa UART decode error: {e}")
                raw = ""
            if raw:
                process_data(raw)
    time.sleep(0.1)
