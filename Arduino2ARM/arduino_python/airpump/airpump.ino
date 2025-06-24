// === 腳位定義 ===
const int AIRPUMP_IN2 = 5;   // 空氣泵馬達 IN2
const int AIRPUMP_IN1 = 6;   // 空氣泵馬達 IN1
const int AIRPUMP_ENA = 7;   // 空氣泵馬達 ENA (PWM)
const int AIRPUMP_PWM = 130; // 空氣泵 PWM 速度
//
// 空氣泵狀態
int airpumpPhase = 0;        // 0: 初始狀態  1: 充氣  2:停止

void setup() {
  pinMode(AIRPUMP_IN1, OUTPUT); 
  pinMode(AIRPUMP_IN2, OUTPUT); 
  pinMode(AIRPUMP_ENA, OUTPUT);
  delay(1000);
}

// 啟動空氣泵
void airpumpStart() {
  digitalWrite(AIRPUMP_IN1, HIGH);
  digitalWrite(AIRPUMP_IN2, LOW);
  analogWrite(AIRPUMP_ENA, AIRPUMP_PWM);
}

// 停止空氣泵
void airpumpStop() {
  digitalWrite(AIRPUMP_IN1, LOW);
  digitalWrite(AIRPUMP_IN2, LOW);
  analogWrite(AIRPUMP_ENA, 0);
}

void loop() {
  // 1.(安全保護, !!勿動!!)
  if (AIRPUMP_PWM < 140 && airpumpPhase == 0){airpumpPhase = 1;}
  else if (AIRPUMP_PWM >= 140) {Serial.println("airpump too fast,打氣馬達太快了!!!");}

  // 2.(空氣泵充氣)
  if (airpumpPhase == 1){
    airpumpStart();
    delay(1500);
    airpumpStop();
    delay(1000);
    airpumpStart();
    delay(3000);
    airpumpStop();
    delay(500);
    airpumpStart();
    delay(2000);
    airpumpStop();
    delay(800);
    airpumpPhase = 2;
    }
}
