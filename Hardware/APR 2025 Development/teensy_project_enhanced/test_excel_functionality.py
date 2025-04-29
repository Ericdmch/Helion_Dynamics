#!/usr/bin/env python3
"""
Test script for the Teensy Data Logger Excel functionality.

This script generates simulated sensor data and tests the Excel and graph generation
capabilities of the enhanced Teensy Data Logger without requiring actual hardware.
"""

import os
import time
import random
import datetime
import math
import sys
from pathlib import Path

# Import the TeensyDataLogger class from the enhanced logger
try:
    # First try to import from the same directory
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from teensy_data_logger_excel import TeensyDataLogger
except ImportError:
    print("Error: Could not import TeensyDataLogger from teensy_data_logger_excel.py")
    print("Make sure the file exists and is in the correct location.")
    sys.exit(1)

class TeensyDataLoggerTester:
    """Class to test the TeensyDataLogger Excel functionality with simulated data."""
    
    def __init__(self, log_dir="test_logs"):
        """Initialize the tester with a test log directory."""
        self.log_dir = log_dir
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # Create an instance of the TeensyDataLogger
        self.logger = TeensyDataLogger(port=None, log_dir=log_dir)
        
        # Override the connect method to avoid actual serial connection
        self.logger.connect = lambda: True
        self.logger.serial_connection = None
        
        # Set a shorter Excel update interval for testing
        self.logger.excel_update_interval = 5
        
        # Initialize simulated data parameters
        self.timestamp = time.time()
        self.device_time = 0
        self.temperature = 25.0
        self.humidity = 50.0
        self.pressure = 1013.25
        self.gas = 100.0
        self.light = 500
        
        # Initialize simulated motion data
        self.accel_x = 0.0
        self.accel_y = 0.0
        self.accel_z = 1.0  # 1g due to gravity
        self.gyro_x = 0.0
        self.gyro_y = 0.0
        self.gyro_z = 0.0
        
        # Signal quality
        self.rssi = -70
        self.snr = 10
    
    def generate_simulated_data(self):
        """Generate simulated sensor data with realistic variations."""
        # Update timestamp and device time
        self.timestamp = time.time()
        self.device_time += 1000  # 1 second in ms
        
        # Add some random variations to the data
        self.temperature += random.uniform(-0.2, 0.2)
        self.humidity += random.uniform(-1.0, 1.0)
        self.pressure += random.uniform(-0.5, 0.5)
        self.gas += random.uniform(-5.0, 5.0)
        self.light += random.randint(-20, 20)
        
        # Add some sinusoidal variations for more realistic patterns
        time_factor = self.device_time / 10000  # Slow oscillation
        self.temperature += 0.5 * math.sin(time_factor)
        self.humidity += 2.0 * math.sin(time_factor * 0.7)
        self.pressure += 1.0 * math.sin(time_factor * 0.5)
        
        # Keep values in realistic ranges
        self.temperature = max(10.0, min(35.0, self.temperature))
        self.humidity = max(20.0, min(80.0, self.humidity))
        self.pressure = max(990.0, min(1030.0, self.pressure))
        self.gas = max(50.0, min(300.0, self.gas))
        self.light = max(0, min(1023, self.light))
        
        # Simulate some motion
        self.accel_x = 0.1 * math.sin(time_factor * 2)
        self.accel_y = 0.1 * math.cos(time_factor * 2)
        self.accel_z = 1.0 + 0.05 * math.sin(time_factor)
        
        self.gyro_x = 5.0 * math.sin(time_factor * 3)
        self.gyro_y = 5.0 * math.cos(time_factor * 3)
        self.gyro_z = 2.0 * math.sin(time_factor * 1.5)
        
        # Simulate signal quality variations
        self.rssi = -70 + random.randint(-10, 5)
        self.snr = 10 + random.randint(-2, 2)
        
        # Format the data as it would come from the Teensy
        data_string = (
            f"TIME:{self.device_time},ADDR:1,RSSI:{self.rssi},SNR:{self.snr},"
            f"T:{self.temperature:.2f},P:{self.pressure:.2f},H:{self.humidity:.2f},G:{self.gas:.2f},"
            f"AX:{self.accel_x:.2f},AY:{self.accel_y:.2f},AZ:{self.accel_z:.2f},"
            f"GX:{self.gyro_x:.2f},GY:{self.gyro_y:.2f},GZ:{self.gyro_z:.2f},L:{self.light}"
        )
        
        return data_string
    
    def run_test(self, num_samples=50, delay=0.5):
        """Run the test by generating simulated data and processing it."""
        print(f"Starting Excel functionality test with {num_samples} simulated data points")
        print(f"Log directory: {self.log_dir}")
        print(f"Excel update interval: {self.logger.excel_update_interval} data points")
        print(f"Delay between samples: {delay} seconds")
        print("-" * 50)
        
        try:
            for i in range(1, num_samples + 1):
                # Generate simulated data
                data_string = self.generate_simulated_data()
                
                # Parse the data
                data_dict = self.logger.parse_data(data_string)
                
                # Log and display the data
                self.logger.log_data(data_dict)
                self.logger.display_data(data_dict)
                
                # Print progress
                print(f"Generated sample {i}/{num_samples} - ", end="")
                if i % self.logger.excel_update_interval == 0:
                    print("Excel update triggered")
                else:
                    print("Excel update in", 
                          f"{self.logger.excel_update_interval - (i % self.logger.excel_update_interval)} more samples")
                
                # Wait before generating the next sample
                time.sleep(delay)
            
            # Final Excel update to ensure all data is included
            print("\nTest completed. Generating final Excel update and graphs...")
            self.logger.update_excel_file()
            self.logger.generate_graphs()
            
            # Print summary
            print("\nTest Summary:")
            print(f"- Generated {num_samples} simulated data points")
            print(f"- Created CSV file: {self.logger.csv_path}")
            print(f"- Created JSON file: {self.logger.json_path}")
            print(f"- Created Excel file: {self.logger.excel_path}")
            print(f"- Generated graphs in: {self.logger.graph_dir}")
            print("\nTest completed successfully!")
            
        except Exception as e:
            print(f"\nError during test: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True

def main():
    """Main function to run the test."""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Test Teensy Data Logger Excel functionality')
    parser.add_argument('-n', '--num-samples', type=int, default=50,
                        help='Number of simulated data samples to generate (default: 50)')
    parser.add_argument('-d', '--delay', type=float, default=0.5,
                        help='Delay between samples in seconds (default: 0.5)')
    parser.add_argument('-o', '--output-dir', default='test_logs',
                        help='Directory for test output (default: test_logs)')
    
    args = parser.parse_args()
    
    # Create and run the tester
    tester = TeensyDataLoggerTester(log_dir=args.output_dir)
    success = tester.run_test(num_samples=args.num_samples, delay=args.delay)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
