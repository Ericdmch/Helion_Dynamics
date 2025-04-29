"""
LoRa Communication Protocol Implementation
- Defines packet structure for Teensy 4.0 to Teensy 4.1 communication
- Implements error checking and reliable transmission
- Handles acknowledgment and retransmission
"""
import time
import struct
import binascii

class LoRaProtocol:
    """
    A class to handle LoRa communication protocol between Teensy 4.0 and Teensy 4.1
    """
    
    def __init__(self, uart, address, destination, debug=False):
        """
        Initialize the LoRa protocol handler
        
        Args:
            uart: The UART object connected to the RYLR998 module
            address: The address of this device
            destination: The address of the destination device
            debug: Enable debug output
        """
        self.uart = uart
        self.address = address
        self.destination = destination
        self.debug = debug
        self.sequence_number = 0
        self.last_received_seq = -1
        self.retries = 3
        self.timeout = 5  # seconds
        
    def _log(self, message):
        """Print debug messages if debug is enabled"""
        if self.debug:
            print(f"LoRa: {message}")
    
    def send_at_command(self, command, wait_time=1):
        """
        Send AT command to the LoRa module and wait for response
        
        Args:
            command: The AT command to send
            wait_time: Time to wait for response in seconds
            
        Returns:
            The response string from the module
        """
        self._log(f"Sending: {command}")
        self.uart.write(f"{command}\r\n".encode())
        time.sleep(wait_time)
        
        response = b""
        while self.uart.in_waiting:
            response += self.uart.read(self.uart.in_waiting)
        
        response_str = response.decode('utf-8', 'ignore').strip()
        self._log(f"Response: {response_str}")
        return response_str
    
    def initialize(self, network_id, band, parameters):
        """
        Initialize the LoRa module with the specified settings
        
        Args:
            network_id: The network ID to use
            band: The frequency band in Hz
            parameters: The RF parameters string
            
        Returns:
            True if initialization was successful, False otherwise
        """
        self._log("Initializing LoRa module...")
        time.sleep(1)  # Give the module time to power up
        
        # Test AT command
        response = self.send_at_command("AT")
        if "+OK" not in response:
            self._log("LoRa module not responding")
            return False
        
        # Configure LoRa module
        self.send_at_command(f"AT+ADDRESS={self.address}")
        self.send_at_command(f"AT+NETWORKID={network_id}")
        self.send_at_command(f"AT+BAND={band}")
        self.send_at_command(f"AT+PARAMETER={parameters}")
        
        self._log("LoRa module initialized")
        return True
    
    def calculate_crc(self, data):
        """
        Calculate CRC-32 checksum for data
        
        Args:
            data: The data to calculate CRC for
            
        Returns:
            CRC-32 checksum as an integer
        """
        return binascii.crc32(data.encode()) & 0xFFFFFFFF
    
    def send_packet(self, data, with_ack=True):
        """
        Send a data packet with optional acknowledgment
        
        Args:
            data: The data string to send
            with_ack: Whether to wait for acknowledgment
            
        Returns:
            True if the packet was sent and acknowledged (if with_ack=True),
            False otherwise
        """
        # Increment sequence number
        self.sequence_number = (self.sequence_number + 1) % 256
        
        # Calculate CRC
        crc = self.calculate_crc(data)
        
        # Create packet: SEQ|DATA|CRC
        packet = f"{self.sequence_number}|{data}|{crc}"
        
        # Send the packet
        for attempt in range(self.retries):
            self._log(f"Sending packet (attempt {attempt+1}/{self.retries}): {packet[:20]}...")
            
            command = f"AT+SEND={self.destination},{len(packet)},{packet}"
            response = self.send_at_command(command)
            
            if "+OK" not in response:
                self._log("Failed to send packet")
                time.sleep(1)
                continue
            
            if not with_ack:
                return True
            
            # Wait for acknowledgment
            ack_received = self._wait_for_ack(self.sequence_number)
            if ack_received:
                self._log("Packet acknowledged")
                return True
            
            self._log("No acknowledgment received, retrying...")
            time.sleep(1)
        
        self._log("Failed to send packet after retries")
        return False
    
    def _wait_for_ack(self, seq_num):
        """
        Wait for acknowledgment of a specific sequence number
        
        Args:
            seq_num: The sequence number to wait for
            
        Returns:
            True if acknowledgment was received, False otherwise
        """
        start_time = time.monotonic()
        
        while time.monotonic() - start_time < self.timeout:
            if self.uart.in_waiting:
                response = b""
                while self.uart.in_waiting:
                    response += self.uart.read(self.uart.in_waiting)
                
                response_str = response.decode('utf-8', 'ignore').strip()
                self._log(f"Received: {response_str}")
                
                # Check if it's an ACK message
                # Format: +RCV=source,length,ACK|seq_num,rssi,snr
                if "+RCV=" in response_str and "ACK|" in response_str:
                    try:
                        parts = response_str.split(',')
                        data_part = parts[2]
                        ack_parts = data_part.split('|')
                        if ack_parts[0] == "ACK" and int(ack_parts[1]) == seq_num:
                            return True
                    except Exception as e:
                        self._log(f"Error parsing ACK: {e}")
            
            time.sleep(0.1)
        
        return False
    
    def receive_packet(self, timeout=1):
        """
        Receive a data packet
        
        Args:
            timeout: Time to wait for a packet in seconds
            
        Returns:
            The received data string, or None if no valid packet was received
        """
        start_time = time.monotonic()
        
        while time.monotonic() - start_time < timeout:
            if self.uart.in_waiting:
                response = b""
                while self.uart.in_waiting:
                    response += self.uart.read(self.uart.in_waiting)
                
                response_str = response.decode('utf-8', 'ignore').strip()
                self._log(f"Received: {response_str}")
                
                # Check if it's a data message
                # Format: +RCV=source,length,seq|data|crc,rssi,snr
                if "+RCV=" in response_str and "|" in response_str:
                    try:
                        # Parse the received data
                        parts = response_str.split(',')
                        source = int(parts[0].split('=')[1])
                        
                        # Only process packets from our expected source
                        if source != self.destination:
                            continue
                        
                        # Extract the data portion
                        data_part = parts[2]
                        
                        # Split into sequence, data, and CRC
                        packet_parts = data_part.split('|', 2)
                        if len(packet_parts) != 3:
                            continue
                        
                        seq_num = int(packet_parts[0])
                        data = packet_parts[1]
                        received_crc = int(packet_parts[2])
                        
                        # Verify CRC
                        calculated_crc = self.calculate_crc(data)
                        if calculated_crc != received_crc:
                            self._log(f"CRC mismatch: {calculated_crc} != {received_crc}")
                            continue
                        
                        # Check for duplicate packet
                        if seq_num == self.last_received_seq:
                            self._log(f"Duplicate packet received (seq={seq_num})")
                            # Send ACK again
                            self._send_ack(seq_num)
                            continue
                        
                        # Update last received sequence
                        self.last_received_seq = seq_num
                        
                        # Send acknowledgment
                        self._send_ack(seq_num)
                        
                        return data
                    except Exception as e:
                        self._log(f"Error parsing packet: {e}")
            
            time.sleep(0.1)
        
        return None
    
    def _send_ack(self, seq_num):
        """
        Send an acknowledgment for a specific sequence number
        
        Args:
            seq_num: The sequence number to acknowledge
        """
        ack_packet = f"ACK|{seq_num}"
        command = f"AT+SEND={self.destination},{len(ack_packet)},{ack_packet}"
        self.send_at_command(command)
        self._log(f"Sent ACK for sequence {seq_num}")
