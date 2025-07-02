const int VALVE_ENB = 2;     // Solenoid valve ENB (PWM)
const int VALVE_IN4 = 3;     // Solenoid valve IN4
const int VALVE_IN3 = 4;     // Solenoid valve IN3
const int VALVE_PWM = 255;

void setup() {
  pinMode(VALVE_IN3, OUTPUT);   
  pinMode(VALVE_IN4, OUTPUT);   
  pinMode(VALVE_ENB, OUTPUT);
  delay(1000);
}

// Open solenoid valve (exhaust)
void valveOpenExhaust() {
  digitalWrite(VALVE_IN3, LOW);
  digitalWrite(VALVE_IN4, HIGH);
  analogWrite(VALVE_ENB, VALVE_PWM);
}

// Close solenoid valve (seal)
void valveCloseExhaust() {
  digitalWrite(VALVE_IN3, LOW);
  digitalWrite(VALVE_IN4, LOW);
  analogWrite(VALVE_ENB, 0);
}

void loop() {
  valveOpenExhaust(); // Open solenoid valve
  delay(100);         // Valve open for 0.1 second
  valveCloseExhaust();// Close solenoid valve
  delay(100);         // Valve closed for 0.1 second
}
