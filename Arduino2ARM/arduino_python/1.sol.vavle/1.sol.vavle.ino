const int VALVE_ENB = 2;     // 電磁閥 ENB (PWM)
const int VALVE_IN4 = 3;     // 電磁閥 IN4
const int VALVE_IN3 = 4;     // 電磁閥 IN3
const int VALVE_PWM = 255;

void setup() {
  pinMode(VALVE_IN3, OUTPUT);   
  pinMode(VALVE_IN4, OUTPUT);   
  pinMode(VALVE_ENB, OUTPUT);
  delay(1000);
}

// 電磁閥打開
void valveOpenExhaust() {
  digitalWrite(VALVE_IN3, LOW);
  digitalWrite(VALVE_IN4, HIGH);
  analogWrite(VALVE_ENB, VALVE_PWM);
}

// 電磁閥封閉
void valveCloseExhaust() {
  digitalWrite(VALVE_IN3, LOW);
  digitalWrite(VALVE_IN4, LOW);
  analogWrite(VALVE_ENB, 0);
}

void loop() {
  valveOpenExhaust(); // 電磁閥打開
  delay(100);         // 電磁閥打開0.1秒
  valveCloseExhaust();// 電磁閥關閉
  delay(100);         // 電磁閥關閉0.1秒
}
