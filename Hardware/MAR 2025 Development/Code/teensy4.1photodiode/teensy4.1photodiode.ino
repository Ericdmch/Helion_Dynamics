// Define the analog pin where the photodiode module is connected
const int photodiodePin = A10;

void setup() {
  // Initialize Serial communication at 9600 baud rate
  Serial.begin(9600);
}

void loop() {
  // Read the analog value from the photodiode module
  int sensorValue = analogRead(photodiodePin);

  // Calculate the actual voltage (0V to 3.3V)
  float voltage = sensorValue * (3.3 / 1023.0);

  // Calculate the light intensity in percentage (0% to 100%)
  float lightIntensityPercent = (sensorValue / 1023.0) * 100.0;

  // Invert the percentage logic
  float invertedLightIntensityPercent = 100.0 - lightIntensityPercent;

  // Print the values to the Serial Monitor
  Serial.print("Photodiode Value: ");
  Serial.print(sensorValue);
  Serial.print(" | Voltage: ");
  Serial.print(voltage, 2); // Print voltage with 2 decimal places
  Serial.print(" V | Light Intensity: ");
  Serial.print(invertedLightIntensityPercent, 2); // Print inverted percentage with 2 decimal places
  Serial.println(" %");

  // Add a small delay to avoid flooding the Serial Monitor
  delay(100);
}