# Setup Guide for Teensy-based Sensor Data System

## Overview
This document provides a step-by-step guide to setting up the Teensy-based sensor data sender and receiver system. The system consists of two Teensy boards: one acting as the sender and the other as the receiver. The sender collects data from sensors and transmits it via LoRa, while the receiver captures the data and forwards it to a computer for visualization.

## Prerequisites
- Two Teensy 4.0 or 4.1 boards
- LoRa module (e.g., SX1278)
- GPS module
- BME680 sensor
- Breadboard and jumper wires
- USB cables
- Computer with Python installed

## Software Setup

### Installing Mu Editor
1. Visit the [Mu Editor website](https://codewith.mu/)
2. Download the latest version for your operating system
3. Install Mu Editor following the on-screen instructions
4. Launch Mu Editor and select "Teensy" as the device type

### Installing Python Libraries
1. Install Python from [python.org](https://www.python.org/downloads/)
2. Open a terminal or command prompt
3. Install the required libraries using pip:
   ```bash
   pip install pyserial matplotlib
4. Install python libraries into teensy: [Circuitpython Libraries](https://circuitpython.org/libraries/)
- asyncio
- adafruit_gps
- adafruit_bme680
5. If there are any missing module errors,
    ```bash
    pip install NAME_MISSING_MODULE

# Hardware Setup
## Sender Board
- **LoRa Module Connection**:
  - TX → RX1 (pin 27)
  - RX → TX1 (pin 26)
  - 3.3V → 3.3V
  - GND → GND

- **GPS Module Connection**:
  - SDA → SDA (pin 29)
  - SCL → SCL (pin 30)
  - 3.3V → 3.3V
  - GND → GND

- **BME680 Sensor Connection**:
  - SDA → SDA (pin 29)
  - SCL → SCL (pin 30)
  - 3.3V → 3.3V
  - GND → GND

## Receiver Board
- **LoRa Module Connection**:
  - TX → RX1 (pin 27)
  - RX → TX1 (pin 26)
  - 3.3V → 3.3V
  - GND → GND

- **Switch Connection**:
  - One side to digital pin 2
  - Other side to GND

- **LED Connection**:
  - Anode → digital pin 3
  - Cathode → GND (with a current-limiting resistor)

# Code Upload

## Uploading Sender Code
1. Open Mu Editor
2. Copy and paste the [BMEGPS Send.py](/Final_Setup/BMEGPS_Send.py) into a new tab
3. Connect the sender Teensy to your computer via USB
4. Click the "Flash" button to upload the code to the Teensy

## Uploading Receiver Code
1. Open a new tab in Mu Editor
2. Copy and paste the [BMEGPS Recieve.py](/Final_Setup/BMEGPS_Recieve.py) into the new tab
3. Connect the receiver Teensy to your computer via USB
4. Click the "Flash" button to upload the code to the Teensy

### Note that the file name must be *code.py* for the code to automatically run on the teensy.

# Running the System

## Starting the Receiver: All that is needed is to power the board.
