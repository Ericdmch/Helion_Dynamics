#!/usr/bin/env python3
"""
LoRa Communication Test Script

This script helps test and verify communication between Teensy 4.0 transmitter
and Teensy 4.1 receiver using Reyax RLYR988 LoRa modules.

It monitors serial output from both devices simultaneously and provides
real-time analysis of the communication.
"""

import serial
import serial.tools.list_ports
import threading
import time
import argparse
import sys
import re
from datetime import datetime

class LoRaCommTester:
    def __init__(self, transmitter_port=None, receiver_port=None, baud_rate=115200):
        self.transmitter_port = transmitter_port
        self.receiver_port = receiver_port
        self.baud_rate = baud_rate
        
        self.transmitter_serial = None
        self.receiver_serial = None
        
        self.running = False
        self.transmitter_data = []
        self.receiver_data = []
        
        # Statistics
        self.transmitter_packets_sent = 0
        self.receiver_packets_received = 0
        self.last_transmitter_time = 0
        self.last_receiver_time = 0
        self.start_time = time.time()
        
        # Patterns to match in the serial output
        self.transmitter_send_pattern = re.compile(r"Transmitting: AT\+SEND=")
        self.transmitter_ok_pattern = re.compile(r"LoRa Response: \+OK")
        self.receiver_recv_pattern = re.compile(r"TIME:.*,ADDR:.*,RSSI:.*")
    
    def find_ports(self):
        """Find available serial ports and try to identify transmitter and receiver."""
        ports = list(serial.tools.list_ports.comports())
        
        if not ports:
            print("No serial ports found.")
            return False
        
        print("Available serial ports:")
        for i, port in enumerate(ports):
            print(f"{i+1}. {port.device} - {port.description}")
        
        if not self.transmitter_port and not self.receiver_port and len(ports) >= 2:
            print("\nAttempting to auto-detect transmitter and receiver...")
            
            # Try to connect to the first two ports and determine which is which
            try:
                ser1 = serial.Serial(ports[0].device, self.baud_rate, timeout=1)
                ser2 = serial.Serial(ports[1].device, self.baud_rate, timeout=1)
                
                # Wait for some data
                time.sleep(2)
                
                # Read data from both ports
                data1 = ser1.read(ser1.in_waiting).decode('utf-8', errors='ignore')
                data2 = ser2.read(ser2.in_waiting).decode('utf-8', errors='ignore')
                
                # Look for patterns that might identify transmitter vs receiver
                if "Transmitter" in data1 and "Receiver" not in data1:
                    self.transmitter_port = ports[0].device
                    self.receiver_port = ports[1].device
                elif "Receiver" in data1 and "Transmitter" not in data1:
                    self.receiver_port = ports[0].device
                    self.transmitter_port = ports[1].device
                elif "Transmitter" in data2 and "Receiver" not in data2:
                    self.transmitter_port = ports[1].device
                    self.receiver_port = ports[0].device
                elif "Receiver" in data2 and "Transmitter" not in data2:
                    self.receiver_port = ports[1].device
                    self.transmitter_port = ports[0].device
                
                # Close the test connections
                ser1.close()
                ser2.close()
                
                if self.transmitter_port and self.receiver_port:
                    print(f"Auto-detected transmitter on {self.transmitter_port}")
                    print(f"Auto-detected receiver on {self.receiver_port}")
                else:
                    print("Could not auto-detect transmitter and receiver.")
                    return False
                
            except Exception as e:
                print(f"Error during auto-detection: {e}")
                return False
        
        return True
    
    def connect(self):
        """Connect to the transmitter and receiver serial ports."""
        if not self.transmitter_port or not self.receiver_port:
            if not self.find_ports():
                return False
        
        try:
            self.transmitter_serial = serial.Serial(self.transmitter_port, self.baud_rate, timeout=1)
            print(f"Connected to transmitter on {self.transmitter_port}")
        except Exception as e:
            print(f"Error connecting to transmitter: {e}")
            return False
        
        try:
            self.receiver_serial = serial.Serial(self.receiver_port, self.baud_rate, timeout=1)
            print(f"Connected to receiver on {self.receiver_port}")
        except Exception as e:
            print(f"Error connecting to receiver: {e}")
            if self.transmitter_serial:
                self.transmitter_serial.close()
            return False
        
        return True
    
    def disconnect(self):
        """Disconnect from serial ports."""
        if self.transmitter_serial:
            self.transmitter_serial.close()
            self.transmitter_serial = None
        
        if self.receiver_serial:
            self.receiver_serial.close()
            self.receiver_serial = None
    
    def read_transmitter(self):
        """Read data from the transmitter serial port."""
        while self.running:
            try:
                if self.transmitter_serial and self.transmitter_serial.in_waiting:
                    line = self.transmitter_serial.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        print(f"[TX {timestamp}] {line}")
                        self.transmitter_data.append((timestamp, line))
                        
                        # Update statistics
                        if self.transmitter_send_pattern.search(line):
                            self.transmitter_packets_sent += 1
                            self.last_transmitter_time = time.time()
                        
            except Exception as e:
                print(f"Error reading from transmitter: {e}")
                break
            
            time.sleep(0.01)
    
    def read_receiver(self):
        """Read data from the receiver serial port."""
        while self.running:
            try:
                if self.receiver_serial and self.receiver_serial.in_waiting:
                    line = self.receiver_serial.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        print(f"[RX {timestamp}] {line}")
                        self.receiver_data.append((timestamp, line))
                        
                        # Update statistics
                        if self.receiver_recv_pattern.search(line):
                            self.receiver_packets_received += 1
                            self.last_receiver_time = time.time()
                        
            except Exception as e:
                print(f"Error reading from receiver: {e}")
                break
            
            time.sleep(0.01)
    
    def print_statistics(self):
        """Print communication statistics."""
        while self.running:
            time.sleep(5)  # Update every 5 seconds
            
            elapsed_time = time.time() - self.start_time
            minutes, seconds = divmod(int(elapsed_time), 60)
            hours, minutes = divmod(minutes, 60)
            
            print("\n----- Communication Statistics -----")
            print(f"Running time: {hours:02d}:{minutes:02d}:{seconds:02d}")
            print(f"Packets sent by transmitter: {self.transmitter_packets_sent}")
            print(f"Packets received by receiver: {self.receiver_packets_received}")
            
            if self.transmitter_packets_sent > 0:
                success_rate = (self.receiver_packets_received / self.transmitter_packets_sent) * 100
                print(f"Packet success rate: {success_rate:.2f}%")
            
            if self.last_transmitter_time > 0:
                last_tx_seconds = time.time() - self.last_transmitter_time
                print(f"Last transmitter activity: {last_tx_seconds:.1f} seconds ago")
            
            if self.last_receiver_time > 0:
                last_rx_seconds = time.time() - self.last_receiver_time
                print(f"Last receiver activity: {last_rx_seconds:.1f} seconds ago")
            
            print("-------------------------------------\n")
    
    def analyze_communication(self):
        """Analyze the communication and provide recommendations."""
        print("\n----- Communication Analysis -----")
        
        # Check if any packets were sent
        if self.transmitter_packets_sent == 0:
            print("ISSUE: No packets were sent by the transmitter.")
            print("RECOMMENDATION: Check if the transmitter is properly initialized and running.")
        
        # Check if any packets were received
        if self.receiver_packets_received == 0:
            print("ISSUE: No packets were received by the receiver.")
            print("RECOMMENDATIONS:")
            print("1. Verify that both devices have matching LoRa parameters (SF, BW, CR, etc.)")
            print("2. Check that the transmitter is sending to the correct address (should be 2)")
            print("3. Check physical connections and antennas")
            print("4. Try resetting both modules to factory defaults")
        
        # Check success rate
        if self.transmitter_packets_sent > 0:
            success_rate = (self.receiver_packets_received / self.transmitter_packets_sent) * 100
            if success_rate < 50:
                print(f"ISSUE: Low packet success rate ({success_rate:.2f}%).")
                print("RECOMMENDATIONS:")
                print("1. Check for interference or obstacles between devices")
                print("2. Try reducing the distance between devices")
                print("3. Verify antenna connections")
                print("4. Try different LoRa parameters (lower SF for shorter range but better reliability)")
        
        # Check for specific error patterns in the transmitter data
        error_patterns = {
            "AT command error": r"\+ERR=",
            "No response": r"No response from LoRa module",
            "Failed to set": r"Failed to set LoRa"
        }
        
        for error_name, pattern in error_patterns.items():
            error_regex = re.compile(pattern)
            errors = [line for _, line in self.transmitter_data if error_regex.search(line)]
            if errors:
                print(f"ISSUE: Detected {len(errors)} '{error_name}' errors in transmitter output.")
                print(f"EXAMPLE: {errors[0]}")
        
        print("-----------------------------------\n")
    
    def run(self, duration=None):
        """Run the communication test."""
        if not self.connect():
            return False
        
        self.running = True
        self.start_time = time.time()
        
        # Start threads for reading from both serial ports
        transmitter_thread = threading.Thread(target=self.read_transmitter)
        receiver_thread = threading.Thread(target=self.read_receiver)
        stats_thread = threading.Thread(target=self.print_statistics)
        
        transmitter_thread.daemon = True
        receiver_thread.daemon = True
        stats_thread.daemon = True
        
        transmitter_thread.start()
        receiver_thread.start()
        stats_thread.start()
        
        print("\nCommunication test started. Press Ctrl+C to stop.")
        
        try:
            if duration:
                print(f"Test will run for {duration} seconds.")
                time.sleep(duration)
            else:
                # Run until interrupted
                while self.running:
                    time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nTest interrupted by user.")
        finally:
            self.running = False
            
            # Wait for threads to finish
            transmitter_thread.join(timeout=1)
            receiver_thread.join(timeout=1)
            stats_thread.join(timeout=1)
            
            # Analyze the results
            self.analyze_communication()
            
            # Disconnect
            self.disconnect()
            
            print("Test completed.")
        
        return True

def main():
    """Main function to parse arguments and run the test."""
    parser = argparse.ArgumentParser(description='LoRa Communication Test Script')
    parser.add_argument('-t', '--transmitter', help='Serial port for the transmitter')
    parser.add_argument('-r', '--receiver', help='Serial port for the receiver')
    parser.add_argument('-b', '--baud', type=int, default=115200, help='Baud rate (default: 115200)')
    parser.add_argument('-d', '--duration', type=int, help='Test duration in seconds')
    
    args = parser.parse_args()
    
    tester = LoRaCommTester(
        transmitter_port=args.transmitter,
        receiver_port=args.receiver,
        baud_rate=args.baud
    )
    
    success = tester.run(duration=args.duration)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
