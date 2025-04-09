# Teensy 4.0/4.1 LoRa Messaging System

A complete CircuitPython solution for sending and receiving messages between Teensy 4.0 and Teensy 4.1 microcontrollers using RYLR998 LoRa radio modules.

## Overview

This project provides code for a reliable messaging system between Teensy 4.0 and Teensy 4.1 boards using LoRa communication. The system includes:

- **Teensy 4.0 Transmitter**: Sends messages to the Teensy 4.1 receiver
- **Teensy 4.1 Receiver**: Receives messages from the Teensy 4.0 and sends acknowledgments
- **Error Handling Module**: Provides robust error tracking and recovery mechanisms
- **Troubleshooting Guide**: Helps diagnose and resolve common issues

The code is written in CircuitPython and includes support for OLED displays, status LEDs, and button input.

## Hardware Requirements

### Teensy 4.0 (Transmitter)
- Teensy 4.0 microcontroller
- RYLR998 LoRa radio module
- Optional: 0.96" OLED display (I2C, SSD1306)
- Optional: Push button for sending predefined messages
- Optional: Status LED

### Teensy 4.1 (Receiver)
- Teensy 4.1 microcontroller
- RYLR998 LoRa radio module
- Optional: 0.96" OLED display (I2C, SSD1306)
- Optional: Status LED

## Wiring Connections

### RYLR998 LoRa Module (for both Teensy 4.0 and 4.1)
- VCC → 3.3V
- GND → GND
- RXD → TX1 (pin 1)
- TXD → RX1 (pin 0)

### OLED Display (for both Teensy 4.0 and 4.1)
- VCC → 3.3V
- GND → GND
- SDA → SDA (pin 18)
- SCL → SCL (pin 19)

### Button (Teensy 4.0 only)
- One terminal → GND
- Other terminal → Pin 2 (with internal pull-up enabled)

### Status LED (for both Teensy 4.0 and 4.1)
- Anode (+) → Pin 13 (through a current-limiting resistor)
- Cathode (-) → GND

## Software Setup

1. Install CircuitPython on both Teensy boards:
   - Download CircuitPython for [Teensy 4.0](https://circuitpython.org/board/teensy40/)
   - Download CircuitPython for [Teensy 4.1](https://circuitpython.org/board/teensy41/)
   - Follow the installation instructions on the CircuitPython website

2. Install required libraries:
   - adafruit_displayio_ssd1306
   - adafruit_display_text

3. Copy the following files to the Teensy 4.0:
   - `teensy_4_0_transmitter.py` (rename to `code.py`)
   - `error_handling.py`

4. Copy the following files to the Teensy 4.1:
   - `teensy_4_1_receiver.py` (rename to `code.py`)
   - `error_handling.py`

## Usage

### Teensy 4.0 (Transmitter)

The transmitter can send messages in two ways:
1. Press the button to cycle through and send predefined messages
2. Connect to the Teensy via USB and type messages in the serial monitor

Serial commands:
- Type a message and press Enter to send it
- Type `status` to check system status
- Type `reset` to reset the system
- Type AT commands (e.g., `AT+VER`) to communicate directly with the LoRa module

### Teensy 4.1 (Receiver)

The receiver automatically listens for incoming messages and displays them on the OLED screen.

Serial commands:
- Type `history` to see message history
- Type `clear` to clear message history
- Type `signal` to check signal strength
- Type `status` to check system status
- Type `reset` to reset the system
- Type AT commands (e.g., `AT+VER`) to communicate directly with the LoRa module

## Enhanced Versions

Enhanced versions of both the transmitter and receiver are provided with additional features:
- Robust error handling and recovery
- System health monitoring
- LED status indicators
- Acknowledgment tracking
- Message retries
- Signal strength monitoring

To use the enhanced versions:
1. Copy `teensy_4_0_transmitter_enhanced.py` to the Teensy 4.0 (rename to `code.py`)
2. Copy `teensy_4_1_receiver_enhanced.py` to the Teensy 4.1 (rename to `code.py`)
3. Copy `error_handling.py` to both Teensy boards

## Troubleshooting

See the `troubleshooting_guide.md` file for detailed information on diagnosing and resolving common issues.

Common issues addressed include:
- LoRa module connection problems
- Message transmission failures
- Display issues
- Button and LED problems
- Serial communication issues

## Customization

### Changing LoRa Parameters

You can modify these constants in both transmitter and receiver code:
```python
LORA_ADDRESS = 1           # Address of this device (Teensy 4.0)
LORA_DESTINATION = 2       # Address of receiver (Teensy 4.1)
LORA_NETWORK_ID = 18       # Network ID (must be same for both devices)
LORA_BAND = 915000000      # Frequency in Hz (915MHz for US)
LORA_PARAMETERS = "9,7,1,12"  # SF=9, BW=125kHz, CR=4/5, Preamble=12
```

Note: Make sure both devices use the same NETWORK_ID and compatible parameters.

### Changing Predefined Messages

Modify the `messages` list in the transmitter code:
```python
messages = [
    "Hello from Teensy 4.0!",
    "This is a test message",
    "LoRa communication test",
    "How's the signal strength?",
    "Message received? Please confirm."
]
```

## License

This project is released under the MIT License.

## Credits

Created by Manus, April 2025.
