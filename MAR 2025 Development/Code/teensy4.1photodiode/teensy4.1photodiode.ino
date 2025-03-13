const int photodiodePin = A13;  // Analog pin connected to photodiode circuit
const int ledPin = 13;          // Digital pin for LED
float voltage = 0;
float lightIntensity = 0;
bool ledState = false;

void setup() {
  Serial.begin(115200);  // Start serial communication
  analogReadResolution(12);  // Set ADC resolution (if using Teensy)
  pinMode(ledPin, OUTPUT);   // Set LED pin as output
}

void loop() {
  // Read analog value (0-4095 for 12-bit resolution)
  int rawValue = analogRead(photodiodePin);
  
  // Convert raw value to voltage (assuming 3.3V reference)
  voltage = (rawValue * 3.3) / 4095.0;
  
  // Depending on your circuit, you might need to invert the logic
  // Option 1: Higher raw value = more light (common for photodiode in reverse bias)
  lightIntensity = map(rawValue, 0, 4095, 0, 100);
  
  // Option 2: Lower raw value = more light (if using a different configuration)
  // lightIntensity = map(4095 - rawValue, 0, 4095, 0, 100);
  
  // Toggle LED state
  ledState = !ledState;
  digitalWrite(ledPin, ledState);
  
  // Print results to serial monitor
  Serial.print("Raw Value: ");
  Serial.print(rawValue);
  Serial.print(" | Voltage: ");
  Serial.print(voltage, 3);
  Serial.print("V | Light Intensity: ");
  Serial.print(lightIntensity);
  Serial.println("%");
  
  // Short delay to make the blink visible
  delay(50);
  
  // Turn LED off after brief moment
  digitalWrite(ledPin, LOW);
  
  // Additional delay between readings
  delay(50);
}