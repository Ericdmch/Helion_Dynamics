"""
Teensy LoRa Messaging - Troubleshooting Guide
This document provides troubleshooting steps for common issues with the
Teensy 4.0 transmitter and Teensy 4.1 receiver LoRa messaging system.

Author: Manus
Date: April 9, 2025
"""

# Common Issues and Solutions

## LoRa Module Connection Issues

### Symptoms:
- "Failed to initialize LoRa module" message
- No response from AT commands
- "Response timeout" messages

### Solutions:
1. Check physical connections:
   - Ensure TX from Teensy is connected to RX on LoRa module
   - Ensure RX from Teensy is connected to TX on LoRa module
   - Verify power connections (VCC and GND)

2. Check baud rate:
   - Default is 115200, but some modules may use 9600
   - Try changing UART initialization to: `uart = busio.UART(board.TX1, board.RX1, baudrate=9600, timeout=SERIAL_TIMEOUT)`

3. Reset the module:
   - Disconnect and reconnect power to the LoRa module
   - Use the AT+FACTORY command to reset to factory settings

## Message Transmission Issues

### Symptoms:
- "Failed to send message" errors
- No acknowledgment received
- Receiver doesn't get messages

### Solutions:
1. Verify matching parameters on both devices:
   - NETWORK_ID must be identical on both devices
   - BAND setting must be appropriate for your region
   - PARAMETER settings must match on both devices

2. Check addressing:
   - Transmitter ADDRESS should be 1
   - Receiver ADDRESS should be 2
   - Ensure transmitter is sending to address 2
   - Ensure receiver is acknowledging to address 1

3. Distance and interference:
   - Reduce distance between devices for testing
   - Move away from sources of interference
   - Try different SF (Spreading Factor) values in PARAMETER setting
     - Higher SF (e.g., 12) gives longer range but slower data rate
     - Lower SF (e.g., 7) gives faster data rate but shorter range

## Display Issues

### Symptoms:
- "Display initialization failed" message
- No visual output on OLED
- Garbled display

### Solutions:
1. Check I2C connections:
   - Verify SDA and SCL connections
   - Ensure proper power to the display

2. Check I2C address:
   - Default is 0x3C, but some displays use 0x3D
   - Try changing the address in the code: `display_bus = displayio.I2CDisplay(i2c, device_address=0x3D)`

3. Reset the display:
   - Power cycle the display
   - Ensure displayio.release_displays() is called before initialization

## Button Issues (Transmitter)

### Symptoms:
- Button press doesn't send messages
- Multiple messages sent with one press

### Solutions:
1. Check button connections:
   - Verify pin connection
   - Check if pull-up resistor is needed

2. Adjust debounce timing:
   - Increase debounce delay if multiple messages are sent
   - Default is 0.5 seconds, try increasing to 1.0 second:
     `time.sleep(1.0)  # Debounce`

## LED Issues (Receiver)

### Symptoms:
- LED doesn't flash when messages are received

### Solutions:
1. Check LED connections:
   - Verify pin connection
   - Ensure LED is connected with correct polarity

2. Increase LED on-time:
   - Make LED flash longer and brighter:
     ```
     led.value = True
     time.sleep(0.5)  # Longer flash
     led.value = False
     ```

## Serial Communication Issues

### Symptoms:
- Can't send commands via serial
- No output in serial monitor

### Solutions:
1. Check serial connection:
   - Ensure proper USB connection
   - Verify correct COM port in serial monitor
   - Set baud rate to 115200 in serial monitor

2. Reset the Teensy:
   - Press reset button on Teensy
   - Reconnect USB cable

## Advanced Troubleshooting

### Signal Strength Testing:
Add this code to the receiver to continuously display signal strength:

```python
def monitor_signal_strength():
    """Request and display current signal strength"""
    response = send_at_command("AT+RSSI?")
    if response and "+RSSI" in response:
        try:
            rssi = response.split(":")[1].strip()
            print(f"Current RSSI: {rssi} dBm")
            update_display("Signal Strength", f"RSSI: {rssi} dBm")
            return rssi
        except Exception as e:
            print(f"Error parsing RSSI: {e}")
    return None
```

### Parameter Optimization:
Try different parameter combinations to optimize for your specific environment:

```python
# For longer range, slower data rate:
LORA_PARAMETERS = "12,7,1,12"  # SF=12, BW=125kHz, CR=4/5, Preamble=12

# For shorter range, faster data rate:
LORA_PARAMETERS = "7,7,1,12"   # SF=7, BW=125kHz, CR=4/5, Preamble=12

# For balanced performance:
LORA_PARAMETERS = "9,8,1,12"   # SF=9, BW=250kHz, CR=4/5, Preamble=12
```

### Recovery Mode:
If the system becomes unresponsive, add this recovery function to both transmitter and receiver:

```python
def enter_recovery_mode():
    """Reset everything and enter recovery mode"""
    print("ENTERING RECOVERY MODE")
    # Reset LoRa module
    send_at_command("AT+FACTORY", wait_for_response=False)
    time.sleep(2)
    
    # Reinitialize with minimal settings
    send_at_command(f"AT+ADDRESS={LORA_ADDRESS}")
    send_at_command(f"AT+NETWORKID={LORA_NETWORK_ID}")
    
    # Update display
    update_display("RECOVERY MODE", "Reset in progress")
    
    # Wait for manual reset
    print("System in recovery mode. Press reset button to restart.")
    while True:
        time.sleep(1)
```

Call this function if initialization fails or after multiple failed communication attempts.
