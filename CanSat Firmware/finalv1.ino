 #include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "MPU6050_6Axis_MotionApps20.h"  // Or the appropriate MPU6050 DMP library

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

bool DMPReady = false;  // Set true if DMP init was successful
uint8_t MPUIntStatus;   // Holds actual interrupt status byte from MPU
uint16_t packetSize;    // Expected DMP packet size (default is 42 bytes)
uint8_t FIFOBuffer[64]; // FIFO storage buffer

Quaternion q;           // [w, x, y, z] Quaternion container
VectorFloat gravity;     // [x, y, z] Gravity vector
float ypr[3];           // [yaw, pitch, roll] Yaw/Pitch/Roll container

void setup() {
  // Initialize serial monitor
  Serial.begin(115200);
  while (!Serial);

  // Initialize BME680 sensor
  if (!bme.begin()) {
    Serial.println("BME680 sensor initialization failed");
    while (1);
  }

  // Set BME680 oversampling and filter
  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(320, 150);  // 320*C for 150 ms

  // Initialize MPU6050
  Serial.println(F("Initializing I2C devices..."));
  mpu.initialize();
  if (mpu.testConnection()) {
    Serial.println(F("MPU6050 connection successful"));

    // Initialize DMP
    uint8_t devStatus = mpu.dmpInitialize();
    if (devStatus == 0) {
      mpu.setDMPEnabled(true);
      MPUIntStatus = mpu.getIntStatus();
      packetSize = mpu.dmpGetFIFOPacketSize();
      DMPReady = true;
      Serial.println(F("DMP ready!"));
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
}

void loop() {
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

  // Display sensor data on Serial Monitor
  Serial.print("Yaw: "); Serial.print(ypr[0] * 180/M_PI);
  Serial.print(" Pitch: "); Serial.print(ypr[1] * 180/M_PI);
  Serial.print(" Roll: "); Serial.println(ypr[2] * 180/M_PI);

  Serial.print("Temp: "); Serial.print(bme.temperature); Serial.println(" *C");
  Serial.print("Pressure: "); Serial.print(bme.pressure / 100.0); Serial.println(" hPa");
  Serial.print("Humidity: "); Serial.print(bme.humidity); Serial.println(" %");
  Serial.print("Gas: "); Serial.print(bme.gas_resistance / 1000.0); Serial.println(" KOhms");
  Serial.print("Altitude: "); Serial.print(bme.readAltitude(SEALEVELPRESSURE_HPA)); Serial.println(" m");
  Serial.println();

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

  // Delay before the next reading
  delay(2000);
}