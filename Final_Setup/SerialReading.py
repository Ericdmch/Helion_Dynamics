import serial
import json
import matplotlib.pyplot as plt
from collections import deque
import logging
from functools import wraps
import time
import re

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sensor_monitor.log'),
        logging.StreamHandler()
    ]
)

# Configuration constants
SERIAL_PORT = '/dev/tty.usbmodem1101'
BAUD_RATE = 115200
MAX_RETRIES = 3
RETRY_DELAY = 2
PLOT_UPDATE_INTERVAL = 0.1  # Seconds
BUFFER_SIZE = 200

# Global state containers
state = {
    'serial_conn': None,
    'plot_active': False,
    'data_buffers': {
        'timestamps': deque(maxlen=BUFFER_SIZE),
        'pressure': deque(maxlen=BUFFER_SIZE),
        'temp': deque(maxlen=BUFFER_SIZE)
    }
}

def handle_errors(func):
    """Decorator for comprehensive error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except serial.SerialException as e:
            logging.error(f"Serial error: {e}")
            state['plot_active'] = False
            reconnect_serial()
        except (ValueError, IndexError) as e:
            logging.warning(f"Data parsing error: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}", exc_info=True)
            state['plot_active'] = False
    return wrapper

def init_serial():
    """Initialize serial connection with retries"""
    logging.debug("Attempting to initialize serial connection")
    for attempt in range(MAX_RETRIES):
        try:
            conn = serial.Serial(
                port=SERIAL_PORT,
                baudrate=BAUD_RATE,
                timeout=1
            )
            logging.info(f"Serial connection established on {SERIAL_PORT}")
            return conn
        except serial.SerialException as e:
            logging.warning(f"Connection attempt {attempt+1}/{MAX_RETRIES} failed: {e}")
            time.sleep(RETRY_DELAY)
    logging.error("Failed to establish serial connection after multiple attempts")
    raise serial.SerialException("Failed to establish serial connection")

def reconnect_serial():
    """Re-establish serial connection"""
    logging.info("Attempting to reconnect serial port...")
    if state['serial_conn']:
        try:
            state['serial_conn'].close()
            logging.debug("Closed existing serial connection")
        except Exception as e:
            logging.warning(f"Error closing serial connection: {e}")
    state['serial_conn'] = init_serial()

def init_plots():
    """Initialize matplotlib figures with crash protection"""
    logging.debug("Initializing plots")
    plt.ion()
    fig, axs = plt.subplots(2, 1, figsize=(12, 8))
    fig.suptitle('Sensor Data Monitor - Live Feed')
    
    # Initialize plots
    plots = {
        'pressure': axs[0].plot([], [], 'b-')[0],
        'temp': axs[1].plot([], [], 'r-')[0]
    }
    
    # Set titles and labels
    axs[0].set_title('Pressure Sensor')
    axs[0].set_xlabel('Time')
    axs[0].set_ylabel('Pressure (Pa)')
    
    axs[1].set_title('Temperature Sensor')
    axs[1].set_xlabel('Time')
    axs[1].set_ylabel('Temperature (°C)')
    
    for ax in axs:
        ax.grid(True)
        ax.set_xlim(0, BUFFER_SIZE)
        ax.figure.canvas.draw_idle()
    
    # Define key press event handler
    def on_key_press(event):
        if event.key == 'q':
            logging.info("User requested shutdown (q pressed)")
            state['plot_active'] = False
            plt.close(fig)
    
    fig.canvas.mpl_connect('key_press_event', on_key_press)
    logging.debug("Plots initialized successfully")
    
    # Show the plot window
    plt.show(block=False)
    
    return fig, plots

@handle_errors
def update_plots(fig, plots):
    """Safe plot updating with buffer checks"""
    if not state['plot_active']:
        return
    
    logging.debug("Updating plots")
    buffers = state['data_buffers']
    
    try:
        for key, plot in plots.items():
            if len(buffers[key]) > 0:
                plot.set_data(range(len(buffers[key])), buffers[key])
                ax = plot.axes
                ax.relim()  # Reset the data limits
                ax.autoscale_view()  # Autoscale the view
        
        fig.canvas.draw()
        fig.canvas.flush_events()
        logging.debug("Plots updated successfully")
    except Exception as e:
        logging.error(f"Plot update failed: {e}")
        state['plot_active'] = False
        plt.close(fig)

@handle_errors
def parse_data(line):
    """Robust data parsing with validation"""
    logging.debug(f"Received line: {line}")
    
    # Extract pressure and temperature values
    pressure_match = re.search(r'Pressure: (\d+) Pa', line)
    temp_match = re.search(r'Temperature: ([\d.]+) °C', line)
    
    if pressure_match and temp_match:
        try:
            pressure = int(pressure_match.group(1))
            temp = float(temp_match.group(1))
            
            # Add data to buffers
            state['data_buffers']['pressure'].append(pressure)
            state['data_buffers']['temp'].append(temp)
            logging.debug("Data added to buffers")
            
        except (ValueError, TypeError) as e:
            logging.warning(f"Invalid sensor values: {line} - {e}")

def main_loop():
    """Main processing loop with stability controls"""
    logging.info("Starting main loop")
    fig, plots = init_plots()
    state['plot_active'] = True
    
    last_update = time.time()
    
    while state['plot_active']:
        try:
            # Controlled serial reading
            if state['serial_conn'].in_waiting:
                line = state['serial_conn'].readline()
                if line:
                    parse_data(line.decode('utf-8', errors='replace').strip())
                    logging.debug("Parsed data from serial line")
            
            # Throttled plot updates
            if time.time() - last_update > PLOT_UPDATE_INTERVAL:
                update_plots(fig, plots)
                last_update = time.time()
                logging.debug("Triggered plot update")
            
            time.sleep(0.01)
            
        except KeyboardInterrupt:
            logging.info("User requested shutdown (Ctrl+C)")
            state['plot_active'] = False
        except Exception as e:
            logging.error(f"Main loop error: {e}")
            state['plot_active'] = False

if __name__ == "__main__":
    try:
        logging.info("Initializing serial connection")
        state['serial_conn'] = init_serial()
        main_loop()
    except Exception as e:
        logging.critical(f"Fatal error: {e}")
    finally:
        if state['serial_conn']:
            logging.info("Closing serial connection")
            state['serial_conn'].close()
        plt.close('all')
        logging.info("System shutdown complete")