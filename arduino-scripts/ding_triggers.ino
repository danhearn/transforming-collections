// Define pins
int pins[20] = {18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37};

void setup() {
  Serial.begin(9600);
  delay(10);
  // Initialise pins
  for (int i = 0; i < 20; i++) {
    pinMode(pins[i], OUTPUT);
    digitalWrite(pins[i], HIGH);
  }
}
// Solenoid trigger function
void solenoidTrig(int pin, int delay_time = 100) {
  digitalWrite(pin, LOW);
  delay(delay_time);
  digitalWrite(pin, HIGH);
}

void loop() {
  // Check if data is available to read
  if (Serial.available() > 0) {
    // Read the incoming message
    String incomingMessage = Serial.readStringUntil('\n');
    int value = incomingMessage.toInt(); // Convert to integer

    if (value >= 18 && value <= 37) { // Check for valid pin number
      solenoidTrig(value);
    }
  }
}