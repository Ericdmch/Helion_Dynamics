/*
 * Teensy 4.1 Receiver Code with Debug Mode
 * 
 * This code receives data from a Teensy 4.0 transmitter via Reyax RLYR988 LoRa module
 * and forwards it to a computer through serial communication for logging.
 * Includes enhanced debugging features to troubleshoot communication issues.
 */

// Define pins
#define RLYR988_RX 7             // UART RX pin for RLYR988
#define RLYR988_TX 8             // UART TX pin for RLYR988
#define LED_PIN 13               // Built-in LED for status indication

// Create a hardware serial port for the RLYR988 LoRa module
#define loraSerial Serial2       // Use Serial2 for RLYR988 communication

// Buffer for received data
String receivedData = "";
bool dataReceived = false;

// Variables for timing
unsigned long lastReceivedTime = 0;
const long timeout = 5000;       // Timeout in milliseconds
unsigned long debugPreviousMillis = 0;
const long debugInterval = 5000; // Debug message interval in milliseconds

// Debug mode flag
bool debugMode = true;           // Set to true to enable detailed debugging

// Variables for communication status
int receiveCount = 0;
unsigned long startTime = 0;
String lastCommand = "";
String lastResponse = "";

void setup() {
  // Initialize serial communication with computer
  Serial.begin(115200);
  while (!Serial && millis() < 3000); // Wait for serial port to connect or timeout after 3 seconds
  Serial.println("Teensy 4.1 Receiver Starting with Debug Mode...");
  
  // Initialize LED pin
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);   // Turn on LED during initialization
  
  // Initialize RLYR988 LoRa module
  loraSerial.begin(115200);
  delay(1000);
  
  // Configure RLYR988 LoRa module with error checking
  Serial.println("Configuring LoRa module...");
  
  // Reset the module to factory defaults first
  sendATCommand("AT+FACTORY");
  delay(500);
  
  // Basic AT command to check if module is responsive
  if (!sendATCommand("AT")) {
    Serial.println("LoRa module not responding to AT commands!");
    blinkLED(3, 100); // Error indicator: 3 quick blinks
  }
  
  // Set to transmission mode
  if (!sendATCommand("AT+MODE=0")) {
    Serial.println("Failed to set LoRa mode!");
  }
  
  // Set baud rate
  if (!sendATCommand("AT+IPR=115200")) {
    Serial.println("Failed to set LoRa baud rate!");
  }
  
  // Set RF parameters (SF=10, BW=125kHz, CR=4/5, Preamble=7)
  // IMPORTANT: These must match the transmitter settings exactly
  if (!sendATCommand("AT+PARAMETER=10,7,1,7")) {
    Serial.println("Failed to set LoRa parameters!");
  }
  
  // Set device address to 2 (different from transmitter)
  if (!sendATCommand("AT+ADDRESS=2")) {
    Serial.println("Failed to set LoRa address!");
  }
  
  // Set network ID (same as transmitter)
  if (!sendATCommand("AT+NETWORKID=0")) {
    Serial.println("Failed to set LoRa network ID!");
  }
  
  // Set RF output power to 15 dBm (maximum)
  if (!sendATCommand("AT+CRFOP=15")) {
    Serial.println("Failed to set LoRa RF power!");
  }
  
  // Get and display the module's firmware version
  sendATCommand("AT+VER?");
  
  // Get and display the current configuration
  sendATCommand("AT+PARAMETER?");
  sendATCommand("AT+ADDRESS?");
  sendATCommand("AT+NETWORKID?");
  sendATCommand("AT+CRFOP?");
  
  Serial.println("Initialization complete");
  digitalWrite(LED_PIN, LOW);    // Turn off LED after initialization
  
  // Send a test message to the transmitter
  Serial.println("Sending test message to transmitter...");
  String testMessage = "RECEIVER_READY";
  sendMessage(1, testMessage);
  
  startTime = millis();
  Serial.println("Waiting for data from transmitter...");
}

void loop() {
  unsigned long currentMillis = millis();
  
  // Check for data from LoRa module
  checkLoraData();
  
  // Check for timeout (no data received for a while)
  if (dataReceived && (currentMillis - lastReceivedTime > timeout)) {
    Serial.println("Warning: No data received for " + String(timeout/1000) + " seconds");
    dataReceived = false;
    
    // Send a ping to the transmitter to check connection
    if (debugMode) {
      Serial.println("Sending ping to transmitter...");
      sendMessage(1, "PING");
    }
  }
  
  // Print debug information periodically
  if (debugMode && (currentMillis - debugPreviousMillis >= debugInterval)) {
    debugPreviousMillis = currentMillis;
    printDebugInfo();
  }
}

// Check for and process data from the LoRa module
void checkLoraData() {
  if (loraSerial.available()) {
    String response = loraSerial.readStringUntil('\n');
    response.trim();
    
    lastResponse = response;
    
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
        
        // Update timing and counters
        lastReceivedTime = millis();
        dataReceived = true;
        receiveCount++;
        
        // Blink LED to indicate data reception
        blinkLED(1, 50);
        
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
        
        // Send acknowledgment back to transmitter
        if (debugMode) {
          sendMessage(senderAddress.toInt(), "ACK");
        }
      }
    } else {
      // Print other responses for debugging
      Serial.print("LoRa: ");
      Serial.println(response);
    }
  }
}

// Send AT command to LoRa module and wait for response
bool sendATCommand(String command) {
  Serial.print("Sending command: ");
  Serial.println(command);
  
  lastCommand = command;
  loraSerial.println(command);
  
  // Wait for response with timeout
  unsigned long startTime = millis();
  String response = "";
  bool responseReceived = false;
  
  while (millis() - startTime < 1000 && !responseReceived) {
    if (loraSerial.available()) {
      response = loraSerial.readStringUntil('\n');
      response.trim();
      responseReceived = true;
      lastResponse = response;
    }
    delay(10);
  }
  
  if (responseReceived) {
    Serial.print("Response: ");
    Serial.println(response);
    return (response == "+OK" || response.startsWith("+"));
  } else {
    Serial.println("No response from LoRa module!");
    return false;
  }
}

// Send a message to a specific address
void sendMessage(int address, String message) {
  String command = "AT+SEND=" + String(address) + "," + String(message.length()) + "," + message;
  
  Serial.print("Sending message: ");
  Serial.println(command);
  
  lastCommand = command;
  loraSerial.println(command);
  
  // Wait for and check the response
  unsigned long startTime = millis();
  bool responseReceived = false;
  
  while (millis() - startTime < 1000 && !responseReceived) {
    if (loraSerial.available()) {
      String response = loraSerial.readStringUntil('\n');
      response.trim();
      lastResponse = response;
      
      Serial.print("LoRa Response: ");
      Serial.println(response);
      
      if (response == "+OK" || response.startsWith("+ERR=")) {
        responseReceived = true;
      }
    }
    delay(10);
  }
  
  if (!responseReceived) {
    Serial.println("No response from LoRa module!");
  }
}

// Print debug information
void printDebugInfo() {
  Serial.println("\n----- DEBUG INFORMATION -----");
  Serial.print("Uptime: ");
  Serial.print(millis() / 1000);
  Serial.println(" seconds");
  
  Serial.print("Time since start: ");
  Serial.print((millis() - startTime) / 1000);
  Serial.println(" seconds");
  
  Serial.print("Received packet count: ");
  Serial.println(receiveCount);
  
  Serial.print("Last received time: ");
  if (lastReceivedTime > 0) {
    Serial.print((millis() - lastReceivedTime) / 1000);
    Serial.println(" seconds ago");
  } else {
    Serial.println("Never");
  }
  
  Serial.print("Last command: ");
  Serial.println(lastCommand);
  
  Serial.print("Last response: ");
  Serial.println(lastResponse);
  
  // Check LoRa module status
  Serial.println("\nChecking LoRa module status...");
  sendATCommand("AT+MODE?");
  sendATCommand("AT+ADDRESS?");
  sendATCommand("AT+NETWORKID?");
  sendATCommand("AT+PARAMETER?");
  sendATCommand("AT+CRFOP?");
  
  Serial.println("-----------------------------\n");
}

// Blink LED for visual indication
void blinkLED(int times, int delayMs) {
  for (int i = 0; i < times; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(delayMs);
    digitalWrite(LED_PIN, LOW);
    delay(delayMs);
  }
}
