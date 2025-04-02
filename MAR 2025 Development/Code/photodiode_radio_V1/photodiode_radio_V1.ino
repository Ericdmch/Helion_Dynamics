// Teensy 4.1 (Receiver) - LoRa Receiver
// LoRa Module: RX → Teensy RX5 (Pin 20), TX → Teensy TX5 (Pin 21)
// Baud Rate: 115200 (default for RYLR modules)

void setup() {
  Serial.begin(9600); // Debugging via USB
  Serial5.begin(115200); // LoRa module on Serial5 (RX5=20, TX5=21)

  // Configure LoRa module
  sendATCommand("AT+ADDRESS=2");    // Receiver address = 2
  sendATCommand("AT+NETWORKID=6");  // Network ID = 6
  sendATCommand("AT+BAND=915000000"); // Frequency = 915MHz
  sendATCommand("AT+PARAMETER=9,7,1,12"); // SF9, BW125kHz, CR4/5, Preamble=12
  sendATCommand("AT+CRFOP=14"); // Transmit power = 14dBm
  Serial.println("LoRa Receiver Ready!");
}

void loop() {
  receiveLoRaData(); // Check for incoming data
}

// Receive and parse data
void receiveLoRaData() {
  if (Serial5.available()) {
    String response = Serial5.readString();
    if (response.startsWith("+RCV")) {
      // Parse data format: +RCV=1,4,512,-99,40
      int address = response.substring(5, response.indexOf(",")).toInt();
      String data = response.substring(response.indexOf(",", 5) + 1);
      data = data.substring(0, data.indexOf(',')); // Extract sensor value
      Serial.print("Received: ");
      Serial.println(data);
    }
  }
}

// Send AT commands and read responses
void sendATCommand(String command) {
  Serial5.println(command);
  delay(500);
  String response = "";
  while (Serial5.available()) {
    response += (char)Serial5.read();
  }
  Serial.print("Command: ");
  Serial.print(command);
  Serial.print(" | Response: ");
  Serial.println(response);
}