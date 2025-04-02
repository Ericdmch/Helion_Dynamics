/*
 * Teensy 4.1 Receiver Code
 * 
 * This code receives data from a Teensy 4.0 transmitter via Reyax RLYR988 LoRa module
 * and forwards it to a computer through serial communication for logging.
 * 
 * The data includes:
 * - BME680 environmental sensor readings (temperature, humidity, pressure, gas)
 * - Analog photodiode module readings
 * - MPU6050 accelerometer/gyroscope readings
 */

// Define pins
#define RLYR988_RX 7             // UART RX pin for RLYR988
#define RLYR988_TX 8             // UART TX pin for RLYR988

// Create a hardware serial port for the RLYR988 LoRa module
#define loraSerial Serial2       // Use Serial2 for RLYR988 communication

// Buffer for received data
String receivedData = "";
bool dataReceived = false;

// Variables for timing
unsigned long lastReceivedTime = 0;
const long timeout = 5000;       // Timeout in milliseconds

void setup() {
  // Initialize serial communication with computer
  Serial.begin(115200);
  while (!Serial && millis() < 3000); // Wait for serial port to connect or timeout after 3 seconds
  Serial.println("Teensy 4.1 Receiver Starting...");
  
  // Initialize RLYR988 LoRa module
  loraSerial.begin(115200);
  delay(1000);
  
  // Configure RLYR988 LoRa module
  loraSerial.println("AT");
  delay(100);
  printLoraResponse();
  
  loraSerial.println("AT+MODE=0");  // Set to transmission mode
  delay(100);
  printLoraResponse();
  
  loraSerial.println("AT+IPR=115200"); // Set baud rate
  delay(100);
  printLoraResponse();
  
  loraSerial.println("AT+PARAMETER=10,7,1,7"); // SF=10, BW=125kHz, CR=4/5, Preamble=7
  delay(100);
  printLoraResponse();
  
  loraSerial.println("AT+ADDRESS=2"); // Set device address to 2 (different from transmitter)
  delay(100);
  printLoraResponse();
  
  loraSerial.println("AT+NETWORKID=0"); // Set network ID (same as transmitter)
  delay(100);
  printLoraResponse();
  
  Serial.println("Initialization complete");
  Serial.println("Waiting for data from transmitter...");
}

void loop() {
  // Check for data from LoRa module
  checkLoraData();
  
  // Check for timeout (no data received for a while)
  if (dataReceived && (millis() - lastReceivedTime > timeout)) {
    Serial.println("Warning: No data received for " + String(timeout/1000) + " seconds");
    dataReceived = false;
  }
}

// Check for and process data from the LoRa module
void checkLoraData() {
  if (loraSerial.available()) {
    String response = loraSerial.readStringUntil('\n');
    response.trim();
    
    // Check if it's a data packet (starts with +RCV=)
    if (response.startsWith("+RCV=")) {
      // Parse the received data
      // Format: +RCV=<sender_address>,<data_length>,<data>,<RSSI>,<SNR>
      int firstComma = response.indexOf(',');
      int secondComma = response.indexOf(',', firstComma + 1);
      int thirdComma = response.indexOf(',', secondComma + 1);
      int fourthComma = response.indexOf(',', thirdComma + 1);
      
      if (firstComma != -1 && secondComma != -1 && thirdComma != -1) {
        String senderAddress = response.substring(5, firstComma);
        String dataLength = response.substring(firstComma + 1, secondComma);
        String data = response.substring(secondComma + 1, thirdComma);
        String rssi = "";
        String snr = "";
        
        if (fourthComma != -1) {
          rssi = response.substring(thirdComma + 1, fourthComma);
          snr = response.substring(fourthComma + 1);
        } else {
          rssi = response.substring(thirdComma + 1);
        }
        
        // Update timing
        lastReceivedTime = millis();
        dataReceived = true;
        
        // Format data for serial output to computer
        // Add timestamp and signal quality information
        String formattedData = "TIME:" + String(millis()) + 
                              ",ADDR:" + senderAddress + 
                              ",RSSI:" + rssi;
        
        if (snr.length() > 0) {
          formattedData += ",SNR:" + snr;
        }
        
        formattedData += "," + data;
        
        // Send formatted data to computer via serial
        Serial.println(formattedData);
      }
    } else {
      // Print other responses for debugging
      Serial.print("LoRa: ");
      Serial.println(response);
    }
  }
}

// Print responses from the LoRa module during setup
void printLoraResponse() {
  while (loraSerial.available()) {
    String response = loraSerial.readStringUntil('\n');
    response.trim();
    Serial.print("LoRa Setup: ");
    Serial.println(response);
  }
}
