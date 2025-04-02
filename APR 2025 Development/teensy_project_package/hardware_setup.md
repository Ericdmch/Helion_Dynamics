# Teensy Project - Hardware Setup and Wiring Guide

## Components Required

### Teensy 4.0 Transmitter
- Teensy 4.0 board
- Reyax RLYR988 LoRa module
- BME680 environmental sensor
- Analog photodiode module
- MPU6050 accelerometer/gyroscope
- Breadboard and jumper wires
- Power supply (USB or battery)

### Teensy 4.1 Receiver
- Teensy 4.1 board
- Reyax RLYR988 LoRa module
- USB cable for connection to computer
- Breadboard and jumper wires

## Wiring Diagrams

### Teensy 4.0 Transmitter Connections

#### Reyax RLYR988 LoRa Module
- VCC → 3.3V on Teensy 4.0
- GND → GND on Teensy 4.0
- RXD → Pin 8 on Teensy 4.0 (TX2)
- TXD → Pin 7 on Teensy 4.0 (RX2)

#### BME680 Environmental Sensor (I2C)
- VCC → 3.3V on Teensy 4.0
- GND → GND on Teensy 4.0
- SCL → Pin 19 on Teensy 4.0 (SCL)
- SDA → Pin 18 on Teensy 4.0 (SDA)

#### Analog Photodiode Module
- VCC → 3.3V on Teensy 4.0
- GND → GND on Teensy 4.0
- OUT → Pin A0 on Teensy 4.0 (Analog input)

#### MPU6050 Accelerometer/Gyroscope (I2C)
- VCC → 3.3V on Teensy 4.0
- GND → GND on Teensy 4.0
- SCL → Pin 19 on Teensy 4.0 (SCL) - shared with BME680
- SDA → Pin 18 on Teensy 4.0 (SDA) - shared with BME680

### Teensy 4.1 Receiver Connections

#### Reyax RLYR988 LoRa Module
- VCC → 3.3V on Teensy 4.1
- GND → GND on Teensy 4.1
- RXD → Pin 8 on Teensy 4.1 (TX2)
- TXD → Pin 7 on Teensy 4.1 (RX2)

## Power Considerations
- The Teensy 4.0 transmitter with all sensors and LoRa module may draw significant power
- For portable applications, a 3.7V LiPo battery with a voltage regulator is recommended
- For stationary applications, powering via USB is sufficient
- The Teensy 4.1 receiver can be powered directly from the computer's USB port

## Notes
- Both I2C devices (BME680 and MPU6050) share the same I2C bus (SCL/SDA pins)
- The BME680 has a default I2C address of 0x76 or 0x77
- The MPU6050 has a default I2C address of 0x68 or 0x69
- If address conflicts occur, you may need to use address selection pins or a different I2C bus
- The Teensy 4.0 and 4.1 have multiple hardware serial ports; this project uses Serial2 for the LoRa modules
- The analog photodiode module should be connected to an analog input pin for proper reading
