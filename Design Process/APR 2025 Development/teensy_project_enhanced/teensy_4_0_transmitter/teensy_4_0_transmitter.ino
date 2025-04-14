/*
 * Teensy 4.0 Transmitter Code
 * 
 * This code collects data from:
 * - BME680 environmental sensor (temperature, humidity, pressure, gas)
 * - Analog photodiode module
 * - MPU6050 accelerometer/gyroscope
 * 
 * And transmits the data using a Reyax RLYR988 LoRa module to a Teensy 4.1 receiver.
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

void setup() {
  // Initialize serial communication with computer
  Serial.begin(115200);
  while (!Serial && millis() < 3000); // Wait for serial port to connect or timeout after 3 seconds
  Serial.println("Teensy 4.0 Transmitter Starting...");
  
  // Initialize I2C communication
  Wire.begin();
  
  // Initialize BME680 sensor
  if (!bme.begin()) {
    Serial.println("Could not find a valid BME680 sensor, check wiring!");
    while (1);
  }
  
  // Set up BME680 parameters
  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(320, 150); // 320*C for 150 ms
  
  // Initialize MPU6050
  mpu6050.begin();
  mpu6050.calcGyroOffsets(true); // Calibrate gyroscope
  
  // Initialize RLYR988 LoRa module
  loraSerial.begin(115200);
  delay(1000);
  
  // Configure RLYR988 LoRa module
  loraSerial.println("AT");
  delay(100);
  loraSerial.println("AT+MODE=0");  // Set to transmission mode
  delay(100);
  loraSerial.println("AT+IPR=115200"); // Set baud rate
  delay(100);
  loraSerial.println("AT+PARAMETER=10,7,1,7"); // SF=10, BW=125kHz, CR=4/5, Preamble=7
  delay(100);
  loraSerial.println("AT+ADDRESS=1"); // Set device address
  delay(100);
  loraSerial.println("AT+NETWORKID=0"); // Set network ID
  delay(100);
  loraSerial.println("AT+CRFOP=15"); // Set RF output power to 15 dBm
  delay(100);
  
  Serial.println("Initialization complete");
}

void loop() {
  unsigned long currentMillis = millis();
  
  // Check if it's time to read sensors and transmit data
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    
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
  }
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
  
  loraSerial.println(command);
  
  // Wait for and print any response from the LoRa module
  delay(100);
  while (loraSerial.available()) {
    String response = loraSerial.readStringUntil('\n');
    Serial.print("LoRa Response: ");
    Serial.println(response);
  }
}
