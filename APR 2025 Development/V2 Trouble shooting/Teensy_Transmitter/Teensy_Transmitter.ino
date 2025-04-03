/*
 * Teensy 4.0 Transmitter Code with Debug Mode
 * 
 * This code collects data from:
 * - BME680 environmental sensor (temperature, humidity, pressure, gas)
 * - Analog photodiode module
 * - MPU6050 accelerometer/gyroscope
 * 
 * And transmits the data using a Reyax RLYR988 LoRa module to a Teensy 4.1 receiver.
 * Includes enhanced debugging features to troubleshoot communication issues.
 */

// Include necessary libraries
#include <Wire.h>                // I2C communication
#include <Adafruit_Sensor.h>     // Base sensor library
#include <Adafruit_BME680.h>     // BME680 sensor library
#include <MPU6050_tockn.h>       // MPU6050 sensor library

// Define pins
#define PHOTODIODE_PIN A0        // Analog pin for photodiode
#define RLYR988_RX 7             // UART RX pin for RLYR988
#define RLYR988_TX 8             // UART TX pin for RLYR988
#define LED_PIN 13               // Built-in LED for status indication

// Create sensor objects
Adafruit_BME680 bme;             // BME680 sensor object
MPU6050 mpu6050(Wire);           // MPU6050 sensor object

// Create a hardware serial port for the RLYR988 LoRa module
#define loraSerial Serial2       // Use Serial2 for RLYR988 communication

// Variables to store sensor data
float temperature, humidity, pressure, gasResistance;
float accelX, accelY, accelZ;
float gyroX, gyroY, gyroZ;
float temperature_mpu;
int lightLevel;

// Variables for timing
unsigned long previousMillis = 0;
const long interval = 1000;      // Transmission interval in milliseconds
unsigned long debugPreviousMillis = 0;
const long debugInterval = 5000; // Debug message interval in milliseconds

// Debug mode flag
bool debugMode = true;           // Set to true to enable detailed debugging

// Variables for communication status
int transmissionCount = 0;
int successCount = 0;
int errorCount = 0;
String lastResponse = "";

void setup() {
  // Initialize serial communication with computer
  Serial.begin(115200);
  while (!Serial && millis() < 3000); // Wait for serial port to connect or timeout after 3 seconds
  Serial.println("Teensy 4.0 Transmitter Starting with Debug Mode...");
  
  // Initialize LED pin
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);   // Turn on LED during initialization
  
  // Initialize I2C communication
  Wire.begin();
  
  // Initialize BME680 sensor
  if (!bme.begin()) {
    Serial.println("Could not find a valid BME680 sensor, check wiring!");
    blinkLED(5, 100); // Error indicator: 5 quick blinks
  } else {
    Serial.println("BME680 sensor initialized successfully");
  }
  
  // Set up BME680 parameters
  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(320, 150); // 320*C for 150 ms
  
  // Initialize MPU6050
  // Modified to avoid using try-catch which isn't supported by default in Arduino
  bool mpu_success = true;
  
  // Try to initialize the MPU6050
  Wire.beginTransmission(0x68); // MPU6050 address
  if (Wire.endTransmission() != 0) {
    mpu_success = false;
  }
  
  if (mpu_success) {
    mpu6050.begin();
    mpu6050.calcGyroOffsets(true); // Calibrate gyroscope
    Serial.println("MPU6050 sensor initialized successfully");
  } else {
    Serial.println("Error initializing MPU6050 sensor, check wiring!");
    blinkLED(4, 100); // Error indicator: 4 quick blinks
  }
  
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
  
  // Set network ID
  if (!sendATCommand("AT+NETWORKID=0")) {
    Serial.println("Failed to set LoRa network ID!");
  }
  
  // Verify network ID
  sendATCommand("AT+NETWORKID?");
  
  // Set device address to 1
  if (!sendATCommand("AT+ADDRESS=1")) {
    Serial.println("Failed to set LoRa address!");
  }
  
  // Verify address
  sendATCommand("AT+ADDRESS?");
  
  // Set RF output power to 15 dBm (maximum)
  if (!sendATCommand("AT+CRFOP=15")) {
    Serial.println("Failed to set LoRa RF power!");
  }
  
  // Verify RF output power
  sendATCommand("AT+CRFOP?");
  
  // Configure LoRa parameters (SF=10, BW=125kHz, CR=4/5, Preamble=7)
  if (!sendATCommand("AT+PARAMETER=10,7,1,7")) {
    Serial.println("Failed to set LoRa parameters!");
  }
  
  // Get and display the module's firmware version
  sendATCommand("AT+VER?");
  
  // Get and display the current configuration
  sendATCommand("AT+PARAMETER?");
  sendATCommand("AT+ADDRESS?");
  sendATCommand("AT+NETWORKID?");
  sendATCommand("AT+CRFOP?");
  
  // Restart the module to apply changes
  sendATCommand("AT+RESET");
  delay(2000);
  
  Serial.println("Initialization complete");
  digitalWrite(LED_PIN, LOW);    // Turn off LED after initialization
  
  // Send a test message to the receiver
  Serial.println("Sending test message to receiver...");
  String testMessage = "T:25.0,P:1013.25,H:50.0,G:100.0,AX:0.0,AY:0.0,AZ:1.0,GX:0.0,GY:0.0,GZ:0.0,L:500";
  transmitData(testMessage);
}

void loop() {
  unsigned long currentMillis = millis();
  
  // Check if it's time to read sensors and transmit data
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    
    // Blink LED to indicate transmission cycle
    digitalWrite(LED_PIN, HIGH);
    
    // Read BME680 sensor
    if (bme.performReading()) {
      temperature = bme.temperature;
      pressure = bme.pressure / 100.0; // Convert to hPa
      humidity = bme.humidity;
      gasResistance = bme.gas_resistance / 1000.0; // Convert to kOhms
    } else {
      Serial.println("Failed to read BME680 sensor!");
      temperature = pressure = humidity = gasResistance = 0;
    }
    
    // Read MPU6050 sensor
    mpu6050.update();
    accelX = mpu6050.getAccX();
    accelY = mpu6050.getAccY();
    accelZ = mpu6050.getAccZ();
    gyroX = mpu6050.getGyroX();
    gyroY = mpu6050.getGyroY();
    gyroZ = mpu6050.getGyroZ();
    temperature_mpu = mpu6050.getTemp();
    
    // Read photodiode
    lightLevel = analogRead(PHOTODIODE_PIN);
    
    // Print sensor data to serial monitor
    Serial.println("Sensor Readings:");
    Serial.print("BME680: Temp="); Serial.print(temperature); Serial.print("°C, ");
    Serial.print("Pressure="); Serial.print(pressure); Serial.print("hPa, ");
    Serial.print("Humidity="); Serial.print(humidity); Serial.print("%, ");
    Serial.print("Gas="); Serial.print(gasResistance); Serial.println("kOhms");
    
    Serial.print("MPU6050: AccX="); Serial.print(accelX); Serial.print("g, ");
    Serial.print("AccY="); Serial.print(accelY); Serial.print("g, ");
    Serial.print("AccZ="); Serial.print(accelZ); Serial.print("g, ");
    Serial.print("GyroX="); Serial.print(gyroX); Serial.print("°/s, ");
    Serial.print("GyroY="); Serial.print(gyroY); Serial.print("°/s, ");
    Serial.print("GyroZ="); Serial.print(gyroZ); Serial.print("°/s, ");
    Serial.print("Temp="); Serial.print(temperature_mpu); Serial.println("°C");
    
    Serial.print("Photodiode: Light="); Serial.println(lightLevel);
    
    // Format data for transmission
    String dataPacket = formatDataPacket();
    
    // Transmit data using RLYR988 LoRa module
    transmitData(dataPacket);
    
    // Turn off LED after transmission
    digitalWrite(LED_PIN, LOW);
  }
  
  // Print debug information periodically
  if (debugMode && (currentMillis - debugPreviousMillis >= debugInterval)) {
    debugPreviousMillis = currentMillis;
    printDebugInfo();
  }
  
  // Check for any incoming messages from the LoRa module
  checkLoraResponse();
}

// Format sensor data into a compact packet for transmission
String formatDataPacket() {
  // Format: "T:{temp},P:{press},H:{hum},G:{gas},AX:{accX},AY:{accY},AZ:{accZ},GX:{gyroX},GY:{gyroY},GZ:{gyroZ},L:{light}"
  String packet = "T:";
  packet += String(temperature, 2);
  packet += ",P:";
  packet += String(pressure, 2);
  packet += ",H:";
  packet += String(humidity, 2);
  packet += ",G:";
  packet += String(gasResistance, 2);
  packet += ",AX:";
  packet += String(accelX, 2);
  packet += ",AY:";
  packet += String(accelY, 2);
  packet += ",AZ:";
  packet += String(accelZ, 2);
  packet += ",GX:";
  packet += String(gyroX, 2);
  packet += ",GY:";
  packet += String(gyroY, 2);
  packet += ",GZ:";
  packet += String(gyroZ, 2);
  packet += ",L:";
  packet += String(lightLevel);
  
  return packet;
}

// Transmit data using RLYR988 LoRa module
void transmitData(String dataPacket) {
  // Send data to address 2 (Teensy 4.1 receiver)
  String command = "AT+SEND=2," + String(dataPacket.length()) + "," + dataPacket;
  
  Serial.print("Transmitting: ");
  Serial.println(command);
  
  transmissionCount++;
  
  // Send the command to the LoRa module
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
      
      if (response == "+OK") {
        successCount++;
        responseReceived = true;
      } else if (response.startsWith("+ERR=")) {
        errorCount++;
        responseReceived = true;
        
        // Parse error code
        int errorCode = response.substring(5).toInt();
        Serial.print("Error code: ");
        Serial.println(errorCode);
        
        // Handle specific error codes
        switch (errorCode) {
          case 1:
            Serial.println("Error: Command format error");
            break;
          case 2:
            Serial.println("Error: Command unavailable in current mode");
            break;
          case 3:
            Serial.println("Error: Parameter error");
            break;
          case 4:
            Serial.println("Error: Parameter out of range");
            break;
          case 5:
            Serial.println("Error: Parameter too long");
            break;
          case 6:
            Serial.println("Error: Operation failed");
            break;
          default:
            Serial.println("Error: Unknown error");
            break;
        }
      }
    }
    delay(10);
  }
  
  if (!responseReceived) {
    Serial.println("No response from LoRa module!");
    errorCount++;
  }
}

// Send AT command to LoRa module and wait for response
bool sendATCommand(String command) {
  Serial.print("Sending command: ");
  Serial.println(command);
  
  loraSerial.println(command);
  
  // Wait for response with timeout
  unsigned long startTime = millis();
  String response = "";
  bool responseReceived = false;
  
  while (millis() - startTime < 2000 && !responseReceived) {
    if (loraSerial.available()) {
      response = loraSerial.readStringUntil('\n');
      response.trim();
      responseReceived = true;
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

// Check for any incoming messages from the LoRa module
void checkLoraResponse() {
  if (loraSerial.available()) {
    String response = loraSerial.readStringUntil('\n');
    response.trim();
    
    Serial.print("Unexpected LoRa message: ");
    Serial.println(response);
    
    // If we receive a message from the receiver, it's a good sign
    if (response.startsWith("+RCV=")) {
      Serial.println("Received acknowledgment from receiver!");
    }
  }
}

// Print debug information
void printDebugInfo() {
  Serial.println("\n----- DEBUG INFORMATION -----");
  Serial.print("Uptime: ");
  Serial.print(millis() / 1000);
  Serial.println(" seconds");
  
  Serial.print("Transmission count: ");
  Serial.println(transmissionCount);
  
  Serial.print("Success count: ");
  Serial.println(successCount);
  
  Serial.print("Error count: ");
  Serial.println(errorCount);
  
  Serial.print("Success rate: ");
  if (transmissionCount > 0) {
    Serial.print((float)successCount / transmissionCount * 100);
    Serial.println("%");
  } else {
    Serial.println("N/A");
  }
  
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