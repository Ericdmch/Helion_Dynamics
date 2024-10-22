#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "MPU6050_6Axis_MotionApps20.h"
#include <Adafruit_GPS.h>

// OLED display width, height, and reset pin
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1

// BME680 setup
#define SEALEVELPRESSURE_HPA (1013.25)
Adafruit_BME680 bme;

// OLED setup
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// MPU6050 setup
MPU6050 mpu;
bool DMPReady = false;  
uint8_t MPUIntStatus;
uint16_t packetSize;
uint8_t FIFOBuffer[64];

Quaternion q;
VectorFloat gravity;
float ypr[3];

// GPS setup
Adafruit_GPS GPS(&Wire);
#define GPS_I2C_ADDR 0x10

// Timing variables
unsigned long lastSwitchTime = 0;
unsigned long switchInterval = 5000;  // 5 seconds interval for screen switching
bool displayGPS = false;  // Flag to toggle between GPS and sensor data display

void setup() {
  // Initialize serial monitor
  Serial.begin(115200);
  while (!Serial);

  // Initialize BME680 sensor
  if (!bme.begin()) {
    Serial.println("BME680 sensor initialization failed");
    while (1);
  }

  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(320, 150); 

  // Initialize MPU6050
  mpu.initialize();
  if (mpu.testConnection()) {
    Serial.println(F("MPU6050 connection successful"));
    uint8_t devStatus = mpu.dmpInitialize();
    if (devStatus == 0) {
      mpu.setDMPEnabled(true);
      packetSize = mpu.dmpGetFIFOPacketSize();
      DMPReady = true;
    } else {
      Serial.print(F("DMP Initialization failed (code "));
      Serial.print(devStatus);
      Serial.println(F(")"));
    }
  } else {
    Serial.println(F("MPU6050 connection failed"));
    while (1);
  }

  // Initialize OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("OLED allocation failed"));
    while (1);
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);

  // Initialize GPS
  GPS.begin(GPS_I2C_ADDR); 
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);  // 1 Hz update rate
}

void loop() {
  // Check for screen switch based on time interval
  if (millis() - lastSwitchTime > switchInterval) {
    displayGPS = !displayGPS;
    lastSwitchTime = millis();
  }

  if (displayGPS) {
    // GPS display section
    displayGPSData();
  } else {
    // Sensor data display section (MPU6050 and BME680)
    displaySensorData();
  }

  delay(100);  // Slight delay for stability
}

void displaySensorData() {
  // Check MPU6050 DMP status
  if (!DMPReady) return;

  // Read a packet from MPU6050 FIFO
  if (mpu.dmpGetCurrentFIFOPacket(FIFOBuffer)) {
    mpu.dmpGetQuaternion(&q, FIFOBuffer);
    mpu.dmpGetGravity(&gravity, &q);
    mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);
  }

  // Get BME680 readings
  if (!bme.performReading()) {
    Serial.println("Failed to perform BME680 reading :(");
    return;
  }

  // Display sensor data on OLED
  display.clearDisplay();
  display.setCursor(0, 0);
  display.print("Yaw: "); display.print(ypr[0] * 180 / M_PI);
  display.setCursor(0, 10);
  display.print("Pitch: "); display.print(ypr[1] * 180 / M_PI);
  display.setCursor(0, 20);
  display.print("Roll: "); display.print(ypr[2] * 180 / M_PI);
  display.setCursor(0, 30);
  display.print("Temp: "); display.print(bme.temperature); display.print(" C");
  display.setCursor(0, 40);
  display.print("Humid: "); display.print(bme.humidity); display.print(" %");
  display.setCursor(0, 50);
  display.print("Pressure: "); display.print(bme.pressure / 100.0); display.print(" hPa");
  display.display();
}

void displayGPSData() {
  char c = GPS.read();
  // Check if GPS data is available
  if (GPS.newNMEAreceived()) {
    if (!GPS.parse(GPS.lastNMEA())) {
      return; // unsuccessful parse
    }
  }

  // Display GPS data on OLED
  display.clearDisplay();
  display.setCursor(0, 0);

  if (GPS.fix) {
    // If GPS fix is available, display coordinates
    display.print("Lat: "); display.println(GPS.latitude, 4);
    display.print("Lon: "); display.println(GPS.longitude, 4);
    display.print("Alt: "); display.print(GPS.altitude); display.println(" m");
    display.print("Sat: "); display.print((int)GPS.satellites);
  } else {
    // If no GPS fix, display error message
    display.print("GPS not connected");
  }

  display.display();
}