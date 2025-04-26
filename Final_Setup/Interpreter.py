import serial
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import numpy as np
import pandas as pd
from datetime import datetime

# --- User Calibration Prompt ---
offset_input = input("Enter temperature offset in °C (e.g. -5.0 for sensor calibration): ").strip()
try:
    temp_offset = float(offset_input)
except ValueError:
    print(f"Invalid offset '{offset_input}', defaulting to 0.0°C")
    temp_offset = 0.0
print(f"Using temperature offset: {temp_offset}°C")

# --- Serial Port Settings ---
PORT       = '/dev/tty.usbmodem101'  # <-- change to your port
BAUD_RATE  = 9600
MAX_POINTS = 200  # rolling window

ser = serial.Serial(PORT, BAUD_RATE, timeout=1)

# Data buffers for plotting
time_data    = deque(maxlen=MAX_POINTS)
temp_data    = deque(maxlen=MAX_POINTS)
press_data   = deque(maxlen=MAX_POINTS)
ax_data      = deque(maxlen=MAX_POINTS)
ay_data      = deque(maxlen=MAX_POINTS)
az_data      = deque(maxlen=MAX_POINTS)
axyz_data    = deque(maxlen=MAX_POINTS)
lat_data     = deque(maxlen=MAX_POINTS)
lon_data     = deque(maxlen=MAX_POINTS)
reading_data = deque(maxlen=MAX_POINTS)
rel_alt_data = deque(maxlen=MAX_POINTS)

# Will accumulate every parsed row here
records = []

# Create subplots (5 rows × 2 cols)
fig, axs = plt.subplots(5, 2, figsize=(15, 12))
fig.tight_layout(pad=3.0)

def update(frame):
    line = ser.readline().decode('utf-8', errors='ignore').strip()
    if not line or not line.startswith('['):
        print(f"⚠️  Skipped non-JSON line: {line}")
        return

    try:
        data = json.loads(line)
        if len(data) != 10:
            raise ValueError("wrong length")

        ts, raw_temp, pressure, Ax, Ay, Az, lat, lon, fluor, rel_alt = data
        # Apply user-specified offset
        temp_calibrated = raw_temp + temp_offset
        axyz = np.sqrt(Ax**2 + Ay**2 + Az**2)

        # Append to plotting buffers
        time_data.append(ts)
        temp_data.append(temp_calibrated)
        press_data.append(pressure)
        ax_data.append(Ax); ay_data.append(Ay); az_data.append(Az)
        axyz_data.append(axyz)
        lat_data.append(lat); lon_data.append(lon)
        reading_data.append(fluor)
        rel_alt_data.append(rel_alt)

        # Log into our record list\ n
        records.append({
            'timestamp': ts,
            'temperature': temp_calibrated,
            'pressure': pressure,
            'Ax': Ax,
            'Ay': Ay,
            'Az': Az,
            'Axyz': axyz,
            'latitude': lat,
            'longitude': lon,
            'fluorometer': fluor,
            'rel_altitude': rel_alt
        })

        # --- redraw each axis ---
        axs[0, 0].cla()
        axs[0, 0].plot(time_data, temp_data)
        axs[0, 0].set_title("Temperature vs Time")

        axs[0, 1].cla()
        axs[0, 1].plot(time_data, press_data)
        axs[0, 1].set_title("Pressure vs Time")

        axs[1, 0].cla()
        axs[1, 0].plot(time_data, ax_data, label='Ax')
        axs[1, 0].plot(time_data, ay_data, label='Ay')
        axs[1, 0].plot(time_data, az_data, label='Az')
        axs[1, 0].set_title("Ax, Ay, Az vs Time")
        axs[1, 0].legend()

        axs[1, 1].cla()
        axs[1, 1].plot(time_data, axyz_data)
        axs[1, 1].set_title("Axyz vs Time")

        axs[2, 0].cla()
        axs[2, 0].plot(time_data, reading_data)
        axs[2, 0].set_title("Fluorometer vs Time")

        axs[2, 1].cla()
        axs[2, 1].plot(time_data, rel_alt_data)
        axs[2, 1].set_title("Relative Altitude vs Time")

        axs[3, 0].cla()
        axs[3, 0].plot(lon_data, lat_data)
        axs[3, 0].set_title("Longitude vs Latitude")

        axs[3, 1].cla()
        axs[3, 1].plot(rel_alt_data, reading_data)
        axs[3, 1].set_title("Fluorometer vs Relative Altitude")

        axs[4, 0].cla()
        axs[4, 0].plot(temp_data, reading_data)
        axs[4, 0].set_title("Fluorometer vs Temperature")

        axs[4, 1].cla()
        axs[4, 1].plot(press_data, reading_data)
        axs[4, 1].set_title("Fluorometer vs Pressure")

        print(f"✅ Successful update : {line}")

    except json.JSONDecodeError:
        print(f"⚠️  Skipped non-JSON line: {line}")
    except ValueError as e:
        print(f"⚠️  Skipped invalid data ({e}): {line}")

# Animate
ani = animation.FuncAnimation(fig, update, interval=500)

# Show and then confirm before saving
plt.show()

# Prompt before exit
confirm = input("Are you sure you want to exit and save data? [y/N]: ").strip().lower()
if confirm in ('y', 'yes'):
    if records:
        # timestamped filename
        now = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"data_log_{now}.xlsx"
        pd.DataFrame(records).to_excel(filename, index=False)
        print(f"\n📄 Saved {len(records)} rows to {filename}")
    else:
        print("\n⚠️  No records to save.")
else:
    print("\n❌ Exit canceled. Data not saved.")






# BLESS THE LORD
# BLESS THE LORD
# BLESS THE LORD
# BLESS THE LORD
# BLESS THE LORD
