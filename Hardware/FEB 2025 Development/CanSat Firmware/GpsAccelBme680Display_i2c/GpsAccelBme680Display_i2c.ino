#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>

#define BME680_ADDRESS 0x77

Adafruit_BME680 bme; // I2C

void setup() {
  Serial.begin(115200);
  while (!Serial);

  // Initialize BME680 sensor
  if (!bme.begin(BME680_ADDRESS)) {
    Serial.println("Could not find a valid BME680 sensor, check wiring!");
    while (1);
  }

  Serial.println("BME680 sensor initialized successfully!");
}

void loop() {
  // Tell BME680 to begin measurement
  unsigned long endTime = bme.beginReading();
  if (endTime == 0) {
    Serial.println("Failed to begin reading :(");
    return;
  }

  // Wait for the measurement to complete
  delay(50); // This represents parallel work

  // Obtain measurement results from BME680
  if (!bme.endReading()) {
    Serial.println("Failed to complete reading :(");
    return;
  }

  // Read data from BME680 sensor
  float temperature = bme.temperature;
  float pressure = bme.pressure / 100.0; // Convert to hPa
  float humidity = bme.humidity;
  float gas_resistance = bme.gas_resistance / 1000.0; // Convert to KOhms

  // Print data to the serial monitor
  Serial.print(temperature); Serial.print(",");
  Serial.print(pressure); Serial.print(",");
  Serial.print(humidity); Serial.print(",");
  Serial.println(gas_resistance);

  delay(200); // Wait 0.2 seconds
}