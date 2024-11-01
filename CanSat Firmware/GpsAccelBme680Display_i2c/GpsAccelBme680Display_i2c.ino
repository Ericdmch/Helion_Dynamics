#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "MPU6050_6Axis_MotionApps20.h"
#include <Adafruit_GPS.h>
#include <EEPROM.h>

// Configuration constants
namespace Config {
    // Display settings
    constexpr uint8_t SCREEN_WIDTH = 128;
    constexpr uint8_t SCREEN_HEIGHT = 64;
    constexpr int8_t OLED_RESET = -1;
    constexpr uint8_t OLED_ADDRESS = 0x3C;
    
    // Timing settings (in milliseconds)
    constexpr unsigned long DISPLAY_SWITCH_INTERVAL = 10000;
    constexpr unsigned long ERROR_DISPLAY_DURATION = 1000;
    constexpr unsigned long SENSOR_READ_INTERVAL = 50;
    constexpr unsigned long GPS_TIMEOUT = 1000;
    
    // Sensor addresses
    constexpr uint8_t GPS_I2C_ADDR = 0x10;
    
    // Error handling
    constexpr uint8_t MAX_INIT_RETRIES = 3;
    constexpr uint8_t MAX_READ_RETRIES = 2;
}

// Sensor status tracking
struct SensorStatus {
    bool bmeReady = false;
    bool mpuReady = false;
    bool gpsReady = false;
    bool displayReady = false;
};

// Global objects
Adafruit_SSD1306 display(Config::SCREEN_WIDTH, Config::SCREEN_HEIGHT, &Wire, Config::OLED_RESET);
Adafruit_BME680 bme;
MPU6050 mpu;
Adafruit_GPS GPS(&Wire);

// Global state
SensorStatus sensorStatus;
unsigned long lastDisplaySwitch = 0;
unsigned long lastSensorRead = 0;
unsigned long lastErrorTime = 0;
bool isDisplayingGPS = false;

// MPU6050 specific variables
bool dmpReady = false;
uint8_t mpuIntStatus;
uint16_t packetSize;
uint8_t fifoBuffer[64];
Quaternion q;
VectorFloat gravity;
float ypr[3];

// Sensor data structure
struct SensorData {
    float temperature;
    float humidity;
    float pressure;
    float yaw;
    float pitch;
    float roll;
    float latitude;
    float longitude;
    float altitude;
    uint8_t satellites;
    bool gpsFixed;
};

SensorData currentData;

class ErrorHandler {
public:
    static void handleError(const char* message, bool fatal = false) {
        Serial.print(F("Error: "));
        Serial.println(message);
        
        display.clearDisplay();
        display.setTextSize(1);
        display.setCursor(0, 0);
        display.println(F("Error:"));
        display.println(message);
        if (fatal) {
            display.println(F("System halted"));
        }
        display.display();
        
        lastErrorTime = millis();
        
        if (fatal) {
            while (true) {
                delay(1000);  // Halt system
            }
        }
    }
};

class SensorHub {
public:
    static bool initialize() {
        Wire.begin();
        Serial.begin(115200);
        
        // Initialize display
        if (!initializeDisplay()) {
            ErrorHandler::handleError("Display init failed", true);
            return false;
        }
        
        // Initialize sensors with retry logic
        for (uint8_t i = 0; i < Config::MAX_INIT_RETRIES; i++) {
            if (initializeBME680() && initializeMPU6050() && initializeGPS()) {
                return true;
            }
            delay(100);
        }
        
        ErrorHandler::handleError("Sensor init failed", true);
        return false;
    }
    
    static void update() {
        if (millis() - lastSensorRead >= Config::SENSOR_READ_INTERVAL) {
            readSensorData();
            lastSensorRead = millis();
        }
        
        updateDisplay();
    }

private:
    static bool initializeDisplay() {
        if (!display.begin(SSD1306_SWITCHCAPVCC, Config::OLED_ADDRESS)) {
            return false;
        }
        display.clearDisplay();
        display.setTextSize(1);
        display.setTextColor(SSD1306_WHITE);
        display.display();
        sensorStatus.displayReady = true;
        return true;
    }
    
    static bool initializeBME680() {
        if (!bme.begin()) {
            return false;
        }
        
        // Configure BME680 settings
        bme.setTemperatureOversampling(BME680_OS_8X);
        bme.setHumidityOversampling(BME680_OS_2X);
        bme.setPressureOversampling(BME680_OS_4X);
        bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
        bme.setGasHeater(320, 150);
        
        sensorStatus.bmeReady = true;
        return true;
    }
    
    static bool initializeMPU6050() {
        mpu.initialize();
        if (!mpu.testConnection()) {
            return false;
        }
        
        uint8_t devStatus = mpu.dmpInitialize();
        if (devStatus != 0) {
            return false;
        }
        
        // Enable DMP
        mpu.setDMPEnabled(true);
        packetSize = mpu.dmpGetFIFOPacketSize();
        dmpReady = true;
        sensorStatus.mpuReady = true;
        return true;
    }
    
    static bool initializeGPS() {
        GPS.begin(Config::GPS_I2C_ADDR);
        GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
        GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);
        
        // Wait for GPS to initialize
        unsigned long startTime = millis();
        while (millis() - startTime < Config::GPS_TIMEOUT) {
            if (GPS.read()) {
                sensorStatus.gpsReady = true;
                return true;
            }
            delay(10);
        }
        return false;
    }
    
    static void readSensorData() {
        // Read BME680
        if (sensorStatus.bmeReady) {
            for (uint8_t i = 0; i < Config::MAX_READ_RETRIES; i++) {
                if (bme.performReading()) {
                    currentData.temperature = bme.temperature;
                    currentData.humidity = bme.humidity;
                    currentData.pressure = bme.pressure / 100.0;
                    break;
                }
                delay(10);
            }
        }
        
        // Read MPU6050
        if (sensorStatus.mpuReady && dmpReady) {
            if (mpu.dmpGetCurrentFIFOPacket(fifoBuffer)) {
                mpu.dmpGetQuaternion(&q, fifoBuffer);
                mpu.dmpGetGravity(&gravity, &q);
                mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);
                
                currentData.yaw = ypr[0] * 180 / M_PI;
                currentData.pitch = ypr[1] * 180 / M_PI;
                currentData.roll = ypr[2] * 180 / M_PI;
            }
        }
        
        // Read GPS
        if (sensorStatus.gpsReady) {
            if (GPS.newNMEAreceived() && GPS.parse(GPS.lastNMEA())) {
                currentData.gpsFixed = GPS.fix;
                if (GPS.fix) {
                    currentData.latitude = GPS.latitude;
                    currentData.longitude = GPS.longitude;
                    currentData.altitude = GPS.altitude;
                    currentData.satellites = GPS.satellites;
                }
            }
        }
    }
    
    static void updateDisplay() {
        // Check if it's time to switch displays
        if (millis() - lastDisplaySwitch >= Config::DISPLAY_SWITCH_INTERVAL) {
            isDisplayingGPS = !isDisplayingGPS;
            lastDisplaySwitch = millis();
        }
        
        display.clearDisplay();
        display.setCursor(0, 0);
        
        if (isDisplayingGPS && currentData.gpsFixed) {
            displayGPSData();
        } else {
            displaySensorData();
        }
        
        display.display();
    }
    
    static void displaySensorData() {
        display.print(F("Yaw: ")); 
        display.println(currentData.yaw, 1);
        display.print(F("Pitch: ")); 
        display.println(currentData.pitch, 1);
        display.print(F("Roll: ")); 
        display.println(currentData.roll, 1);
        display.print(F("Temp: ")); 
        display.print(currentData.temperature, 1); 
        display.println(F(" C"));
        display.print(F("Humid: ")); 
        display.print(currentData.humidity, 1); 
        display.println(F(" %"));
        display.print(F("Press: ")); 
        display.print(currentData.pressure, 1); 
        display.println(F(" hPa"));
    }
    
    static void displayGPSData() {
        display.print(F("Lat: ")); 
        display.println(currentData.latitude, 4);
        display.print(F("Lon: ")); 
        display.println(currentData.longitude, 4);
        display.print(F("Alt: ")); 
        display.print(currentData.altitude); 
        display.println(F(" m"));
        display.print(F("Sat: ")); 
        display.println(currentData.satellites);
    }
};

void setup() {
    SensorHub::initialize();
}

void loop() {
    SensorHub::update();
}