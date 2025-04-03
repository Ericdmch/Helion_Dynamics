# LoRa Communication Troubleshooting Guide

This guide provides a systematic approach to troubleshoot communication issues between the Teensy 4.0 transmitter and Teensy 4.1 receiver using Reyax RLYR988 LoRa modules.

## Common Issues and Solutions

### 1. Configuration Mismatch

**Problem**: The most common cause of communication failure is mismatched configuration parameters between transmitter and receiver.

**Solution**: Ensure both modules have identical settings for:
- Frequency band
- Spreading factor (SF)
- Bandwidth (BW)
- Coding rate (CR)
- Preamble length
- Network ID

The debug code provided will display these settings. Verify they match exactly.

### 2. Address Configuration

**Problem**: Incorrect address settings can prevent message delivery.

**Solution**:
- Transmitter should be set to address 1 (`AT+ADDRESS=1`)
- Receiver should be set to address 2 (`AT+ADDRESS=2`)
- When sending, the transmitter must specify the receiver's address (2)
- Both must have the same network ID (`AT+NETWORKID=0`)

### 3. Hardware Connection Issues

**Problem**: Incorrect wiring or loose connections can prevent communication.

**Solution**:
- Verify TX/RX connections are correct and not reversed:
  - Teensy TX (pin 8) → RLYR988 RX
  - Teensy RX (pin 7) → RLYR988 TX
- Check power connections (3.3V and GND)
- Ensure all connections are secure
- Try using different pins and updating the code accordingly

### 4. Range and Interference

**Problem**: Distance or obstacles between modules can affect communication.

**Solution**:
- Test with modules in close proximity first (1-2 meters)
- Ensure antennas are properly attached to both modules
- Move away from sources of interference (WiFi routers, Bluetooth devices)
- Set maximum power output (`AT+CRFOP=15`)

### 5. Module Responsiveness

**Problem**: LoRa module may be unresponsive or in an incorrect state.

**Solution**:
- Reset modules to factory defaults (`AT+FACTORY`)
- Power cycle both Teensy boards
- Verify modules respond to basic AT commands
- Check if modules are in the correct mode (`AT+MODE=0`)

## Using the Debug Code

The provided debug code for both transmitter and receiver includes enhanced features to help identify communication issues:

### Transmitter Debug Features

1. **Detailed Initialization**: Verifies each configuration step
2. **Command Response Tracking**: Shows if AT commands are successful
3. **Transmission Status**: Tracks successful vs. failed transmissions
4. **Error Code Interpretation**: Explains LoRa module error codes
5. **Periodic Status Reports**: Shows current configuration and statistics
6. **Visual Indicators**: LED blinks to indicate activity and errors

### Receiver Debug Features

1. **Configuration Verification**: Checks all LoRa settings
2. **Active Listening**: Continuously monitors for incoming messages
3. **Connection Testing**: Sends test messages to verify bidirectional communication
4. **Signal Quality Reporting**: Shows RSSI and SNR values for received messages
5. **Acknowledgment System**: Sends confirmation back to transmitter
6. **Visual Indicators**: LED blinks when data is received

## Step-by-Step Debugging Process

1. **Upload Debug Code**:
   - Upload `teensy_debug_transmitter.ino` to the Teensy 4.0
   - Upload `teensy_debug_receiver.ino` to the Teensy 4.1

2. **Monitor Serial Output**:
   - Connect both Teensy boards to separate USB ports
   - Open two serial monitor windows (115200 baud)
   - Observe initialization messages on both

3. **Verify Module Responsiveness**:
   - Both modules should respond to AT commands during initialization
   - If not, check hardware connections and power

4. **Check Configuration**:
   - Compare the configuration parameters displayed during initialization
   - Ensure they match exactly (especially PARAMETER, ADDRESS, and NETWORKID)

5. **Test Transmission**:
   - The transmitter will send data every second
   - Check if the transmitter reports successful transmission (`+OK` response)
   - Check if the receiver displays any received data

6. **Analyze Debug Information**:
   - Both modules will display debug information every 5 seconds
   - Look for error patterns or configuration mismatches
   - Check signal quality (RSSI and SNR) if messages are received

7. **Test Bidirectional Communication**:
   - The receiver will send acknowledgments when messages are received
   - Check if the transmitter receives these acknowledgments

## Specific Troubleshooting Steps

If no communication is established after the above steps:

1. **Factory Reset Both Modules**:
   - The debug code already does this during initialization
   - Verify that `AT+FACTORY` command receives `+OK` response

2. **Try Different Parameter Settings**:
   - Modify the `AT+PARAMETER` settings in both codes
   - Try a lower spreading factor (SF) for faster transmission:
     - Change `AT+PARAMETER=10,7,1,7` to `AT+PARAMETER=7,7,1,7`

3. **Check for Hardware Issues**:
   - Try connecting the LoRa modules to different pins
   - Update the pin definitions in the code accordingly
   - Try different Teensy boards if available

4. **Verify Module Functionality**:
   - Test each LoRa module individually with simple AT commands
   - Ensure they respond correctly to basic commands like `AT` and `AT+VER?`

5. **Check for Interference**:
   - Try operating in a different location
   - Remove other electronic devices from the vicinity

## Advanced Debugging

If basic troubleshooting doesn't resolve the issue:

1. **Monitor Power Supply**:
   - Ensure stable power to both LoRa modules
   - Try using external power instead of USB power

2. **Check Firmware Version**:
   - Use `AT+VER?` to check firmware versions
   - Ensure both modules have compatible firmware

3. **Test with Different Baud Rate**:
   - Try changing the baud rate to 9600:
     - Update `loraSerial.begin(115200)` to `loraSerial.begin(9600)`
     - Update `AT+IPR=115200` to `AT+IPR=9600`

4. **Increase Timeout Values**:
   - Some modules may need more time to respond
   - Increase timeout values in the sendATCommand function

5. **Try Different Frequency Band**:
   - If available in your region, try different frequency settings
   - Use `AT+BAND=` command to change frequency band

## Hardware Verification

If software troubleshooting doesn't resolve the issue:

1. **Test LoRa Modules Directly**:
   - Connect the LoRa modules directly to a computer using a USB-to-TTL adapter
   - Use a terminal program to send AT commands directly
   - Verify basic functionality without the Teensy boards

2. **Check Antenna Connection**:
   - Ensure antennas are properly connected
   - Try different antennas if available

3. **Measure Voltage Levels**:
   - Use a multimeter to verify proper voltage levels
   - LoRa modules typically require 3.3V

## Conclusion

By systematically working through these troubleshooting steps, you should be able to identify and resolve the communication issues between your Teensy 4.0 transmitter and Teensy 4.1 receiver. The debug code provides detailed information to help pinpoint the exact cause of the problem.

If you continue to experience issues after trying all these steps, consider replacing the LoRa modules as they may be defective.
