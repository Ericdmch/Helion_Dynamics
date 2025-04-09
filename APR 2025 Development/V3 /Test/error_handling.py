"""
Enhanced Error Handling for Teensy 4.0 LoRa Transmitter

This module adds robust error handling and recovery mechanisms to the
Teensy 4.0 transmitter code.

Import this module in the main transmitter code to enable enhanced error handling.
"""

import time
import supervisor

# Error tracking
error_counts = {
    "lora_init": 0,
    "send_failure": 0,
    "no_ack": 0,
    "uart_timeout": 0,
    "display": 0
}

MAX_ERRORS = {
    "lora_init": 3,      # Max consecutive initialization failures
    "send_failure": 5,    # Max consecutive send failures
    "no_ack": 10,         # Max messages without acknowledgment
    "uart_timeout": 8,    # Max UART timeouts
    "display": 5          # Max display errors
}

# Last successful operation timestamps
last_successful = {
    "send": 0,
    "receive_ack": 0,
    "lora_command": 0
}

def track_error(error_type):
    """Track error occurrences and return True if threshold exceeded"""
    if error_type in error_counts:
        error_counts[error_type] += 1
        print(f"Error count for {error_type}: {error_counts[error_type]}/{MAX_ERRORS[error_type]}")
        
        # Check if threshold exceeded
        if error_counts[error_type] >= MAX_ERRORS[error_type]:
            return True
    return False

def reset_error_count(error_type):
    """Reset error count for a specific type"""
    if error_type in error_counts:
        error_counts[error_type] = 0

def reset_all_error_counts():
    """Reset all error counters"""
    for key in error_counts:
        error_counts[key] = 0

def record_success(operation_type):
    """Record timestamp of successful operation"""
    if operation_type in last_successful:
        last_successful[operation_type] = time.monotonic()

def time_since_success(operation_type):
    """Get time elapsed since last successful operation"""
    if operation_type in last_successful and last_successful[operation_type] > 0:
        return time.monotonic() - last_successful[operation_type]
    return float('inf')  # Return infinity if no successful operation recorded

def check_system_health():
    """Check overall system health and return status"""
    # Check if any error thresholds are exceeded
    for error_type, count in error_counts.items():
        if count >= MAX_ERRORS[error_type]:
            return False, f"Error threshold exceeded for {error_type}"
    
    # Check time since last successful operations
    if time_since_success("lora_command") > 300:  # 5 minutes
        return False, "No successful LoRa commands for 5 minutes"
    
    return True, "System healthy"

def watchdog_reset():
    """Force a system reset using the supervisor module"""
    print("WATCHDOG: Forcing system reset...")
    supervisor.reload()

def enter_recovery_mode(uart, display_update_func=None):
    """Reset everything and enter recovery mode"""
    print("ENTERING RECOVERY MODE")
    
    # Reset error counts
    reset_all_error_counts()
    
    # Update display if function provided
    if display_update_func:
        display_update_func("RECOVERY MODE", "Resetting...")
    
    # Try to reset LoRa module
    try:
        uart.write("AT+FACTORY\r\n".encode())
        time.sleep(2)
    except Exception:
        pass
    
    # Wait a moment
    time.sleep(3)
    
    # Try minimal initialization
    try:
        uart.write("AT+RESET\r\n".encode())
        time.sleep(2)
    except Exception:
        pass
    
    # Update display again
    if display_update_func:
        display_update_func("RECOVERY COMPLETE", "Press reset button")
    
    print("Recovery mode complete. Press reset button to restart.")
    print("If problems persist, check physical connections and power cycle the system.")
    
    # Blink to indicate recovery mode
    while True:
        # Blink pattern to indicate recovery mode
        for _ in range(3):
            # We can't assume LED is available, so just wait
            time.sleep(0.2)
        time.sleep(1.0)
