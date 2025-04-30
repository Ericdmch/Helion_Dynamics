#!/usr/bin/env python3
"""
LoRa Communication Test Script (Modified)

This script tests communication between LoRa modules using a specified serial port.
"""

import serial
import argparse
import sys
import re
from datetime import datetime
import time
import threading

class LoRaCommTester:
    def __init__(self, port=None, baud_rate=115200):
        self.port = port
        self.baud_rate = baud_rate
        self.serial_connection = None
        
        self.running = False
        self.data = []
        
        # Statistics
        self.packets_sent = 0
        self.packets_received = 0
        self.last_activity_time = 0
        self.start_time = time.time()
        
        # Patterns to match in the serial output
        self.send_pattern = re.compile(r"Transmitting: AT\+SEND=")
        self.recv_pattern = re.compile(r"TIME:.*,ADDR:.*,RSSI:.*")
    
    def connect(self):
        """Connect to the specified serial port."""
        try:
            self.serial_connection = serial.Serial(self.port, self.baud_rate, timeout=1)
            print(f"Connected to {self.port}")
            return True
        except Exception as e:
            print(f"Error connecting to {self.port}: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the serial port."""
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None
    
    def read_serial(self):
        """Read data from the serial port."""
        while self.running:
            try:
                if self.serial_connection and self.serial_connection.in_waiting:
                    line = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        print(f"[{timestamp}] {line}")
                        self.data.append((timestamp, line))
                        
                        # Update statistics
                        if self.send_pattern.search(line):
                            self.packets_sent += 1
                            self.last_activity_time = time.time()
                        elif self.recv_pattern.search(line):
                            self.packets_received += 1
                            self.last_activity_time = time.time()
                        
            except Exception as e:
                print(f"Error reading from serial port: {e}")
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
            print(f"Packets sent: {self.packets_sent}")
            print(f"Packets received: {self.packets_received}")
            
            if self.packets_sent > 0:
                success_rate = (self.packets_received / self.packets_sent) * 100
                print(f"Packet success rate: {success_rate:.2f}%")
            
            if self.last_activity_time > 0:
                last_activity_seconds = time.time() - self.last_activity_time
                print(f"Last activity: {last_activity_seconds:.1f} seconds ago")
            
            print("-------------------------------------\n")
    
    def analyze_communication(self):
        """Analyze the communication and provide recommendations."""
        print("\n----- Communication Analysis -----")
        
        # Check if any packets were sent
        if self.packets_sent == 0:
            print("ISSUE: No packets were sent.")
            print("RECOMMENDATION: Check if the device is properly initialized and running.")
        
        # Check if any packets were received
        if self.packets_received == 0:
            print("ISSUE: No packets were received.")
            print("RECOMMENDATIONS:")
            print("1. Verify that both devices have matching LoRa parameters (SF, BW, CR, etc.)")
            print("2. Check physical connections and antennas")
            print("3. Try resetting both modules to factory defaults")
        
        # Check success rate
        if self.packets_sent > 0:
            success_rate = (self.packets_received / self.packets_sent) * 100
            if success_rate < 50:
                print(f"ISSUE: Low packet success rate ({success_rate:.2f}%).")
                print("RECOMMENDATIONS:")
                print("1. Check for interference or obstacles between devices")
                print("2. Try reducing the distance between devices")
                print("3. Verify antenna connections")
                print("4. Try different LoRa parameters (lower SF for shorter range but better reliability)")
        
        print("-----------------------------------\n")
    
    def run(self, duration=None):
        """Run the communication test."""
        if not self.connect():
            return False
        
        self.running = True
        self.start_time = time.time()
        
        # Start threads for reading from the serial port
        read_thread = threading.Thread(target=self.read_serial)
        stats_thread = threading.Thread(target=self.print_statistics)
        
        read_thread.daemon = True
        stats_thread.daemon = True
        
        read_thread.start()
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
            read_thread.join(timeout=1)
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
    parser.add_argument('-p', '--port', required=True, help='Serial port for the device')
    parser.add_argument('-b', '--baud', type=int, default=115200, help='Baud rate (default: 115200)')
    parser.add_argument('-d', '--duration', type=int, help='Test duration in seconds')
    
    args = parser.parse_args()
    
    tester = LoRaCommTester(
        port=args.port,
        baud_rate=args.baud
    )
    
    success = tester.run(duration=args.duration)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()