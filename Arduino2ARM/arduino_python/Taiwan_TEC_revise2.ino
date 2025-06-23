// Taiwan_TEC.ino
// =============================
// Arduino 控制空氣泵、步進馬達與電磁閥教學範例
// =============================
// 本程式示範如何以指令控制一組氣動與步進馬達系統，並以註解詳細說明每個步驟。
//
// [硬體連接說明]
// IN1, IN2, ENA: 控制空氣泵馬達（M1）
// IN3, IN4, ENB: 控制電磁閥
// limit1, limit2: 兩個限位開關（安全保護）
// STEP_PIN, DIR_PIN: 步進馬達控制腳位
//
// [指令說明]
// 透過序列埠輸入 A~F 指令，控制馬達旋轉圈數
//
// =============================

// === 腳位定義 ===
const int AIRPUMP_IN1 = 6;   // 空氣泵馬達 IN1
const int AIRPUMP_IN2 = 5;   // 空氣泵馬達 IN2
const int AIRPUMP_ENA = 7;   // 空氣泵馬達 ENA (PWM)
const int VALVE_IN3 = 4;     // 電磁閥 IN3
const int VALVE_IN4 = 3;     // 電磁閥 IN4
const int VALVE_ENB = 2;     // 電磁閥 ENB (PWM)
const int LIMIT1_PIN = 9;    // 限位開關1
const int LIMIT2_PIN = 10;   // 限位開關2
const int STEP_PIN = 12;     // 步進馬達 STEP
const int DIR_PIN = 13;      // 步進馬達 DIR

// === 參數常數 ===
const int STEPS_PER_REV = 200;      // 步進馬達一圈步數
const int AIRPUMP_ON_MS = 400;     // 空氣泵啟動時間 (ms)
const int AIRPUMP_OFF_MS = 2000;    // 空氣泵停止時間 (ms)
const int AIRPUMP_PWM = 130;        // 空氣泵 PWM 速度
const int VALVE_PWM = 255;          // 電磁閥 PWM 速度
const int MAX_STEPS = 1800;        // 步進馬達最大步數（安全）

// === 狀態變數 ===
int totalSteps = 0;                 // 目標步數
String serialInput = "";            // 序列埠輸入指令

// 空氣泵狀態
int airpumpPhase = 0;               // 0: 停止, 1: 充氣
int airpumpCycleCount = 0;          // 充氣/停止循環次數

// 步進馬達狀態
int stepperPhase = 0;               // 0: 停止  1: 正轉  2: 停止與排氣  3: 反轉
int stepperStepCount = 0;           // 已走步數

// =============================
// 初始化
// =============================
void setup() {
  Serial.begin(9600); // 啟動序列通訊
  // 設定所有腳位模式
  pinMode(AIRPUMP_IN1, OUTPUT); pinMode(AIRPUMP_IN2, OUTPUT); pinMode(AIRPUMP_ENA, OUTPUT);
  pinMode(VALVE_IN3, OUTPUT);   pinMode(VALVE_IN4, OUTPUT);   pinMode(VALVE_ENB, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);     pinMode(STEP_PIN, OUTPUT);
  pinMode(LIMIT1_PIN, INPUT_PULLUP); pinMode(LIMIT2_PIN, INPUT_PULLUP);
  delay(1000); // 啟動後延遲 1 秒
}

// =============================
// 控制函式區
// =============================
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
// 步進馬達走一步（速度控制）
void stepperStep() {
  digitalWrite(STEP_PIN, HIGH);
  delayMicroseconds(500); // 控制速度
  digitalWrite(STEP_PIN, LOW);
  delayMicroseconds(500);
}
// 步進馬達正轉一步
void stepperForward() {
  digitalWrite(DIR_PIN, HIGH);
  stepperStep();
}
// 步進馬達反轉一步
void stepperBackward() {
  digitalWrite(DIR_PIN, LOW);
  stepperStep();
}
// 電磁閥封閉（關閉排氣）
void valveCloseExhaust() {
  digitalWrite(VALVE_IN3, LOW);
  digitalWrite(VALVE_IN4, LOW);
  analogWrite(VALVE_ENB, 0);
}
// 電磁閥打開（排氣）
void valveOpenExhaust() {
  digitalWrite(VALVE_IN3, HIGH);
  digitalWrite(VALVE_IN4, LOW);
  analogWrite(VALVE_ENB, VALVE_PWM);
}

// =============================
// 主流程 loop
// =============================
void loop() {
  unsigned long now = millis(); // 取得目前時間

  // 1. 讀取序列埠指令（只在系統閒置時）
  if (Serial.available() && airpumpPhase == 0) {
    serialInput = Serial.readStringUntil('\n');
    serialInput.trim();
  }
  // 2. 執行中時清空序列緩衝區，避免誤讀
  if (airpumpPhase != 0) {
    while (Serial.available()) Serial.read();
  }

  // 3. 處理輸入指令，決定步數
  if (serialInput != "") {
    airpumpPhase = 1;
    if (serialInput == "A" || serialInput == "D") {
      totalSteps = STEPS_PER_REV * 3; // 轉 3 圈
      Serial.println("Go to first box");
    } else if (serialInput == "B" || serialInput == "E") {
      totalSteps = STEPS_PER_REV * 5; // 轉 5 圈
      Serial.println("Go to second box");
    } else if (serialInput == "C" || serialInput == "F") {
      totalSteps = STEPS_PER_REV * 7; // 轉 7 圈
      Serial.println("Go to last box");
    }

  // 4. 安全保護
    if (totalSteps >= STEPS_PER_REV * 9) {
      Serial.println("too many steps");
    }
    serialInput = "";
  }

  // 4. 空氣泵控制
  if (airpumpPhase == 1 && totalSteps > 0 && totalSteps < MAX_STEPS) {
    delay(5000);
    airpumpStart();
    delay(1500);
    airpumpStop();
    delay(500);
    airpumpPhase = 2;
    stepperPhase = 1;
  }

  // 5. 步進馬達正轉
  if (stepperPhase == 1) {
    stepperForward();
    stepperStepCount++;
  }

  // 6. 正轉完成，進入排氣等待
  if (stepperPhase == 1 && stepperStepCount >= totalSteps) {
    stepperPhase = 2;
    delay(1000); // 教學用：觀察
    valveOpenExhaust();
    delay(1000);
    stepperStepCount = 0;
    stepperPhase = 3;
  }
  
  //7. 步進馬達反轉
  if (stepperPhase == 3) {
    stepperBackward();
    stepperStepCount++;
  }

  // 8. 反轉完成或碰到限位，結束流程
  if (stepperPhase == 3 && stepperStepCount >= totalSteps || digitalRead(LIMIT1_PIN) == LOW || digitalRead(LIMIT2_PIN) == LOW) {
    Serial.println("Over");
    delay(1000);
    valveOpenExhaust();
    airpumpPhase = 0;
    airpumpCycleCount = 0;
    stepperPhase = 0;
    stepperStepCount = 0;
    valveCloseExhaust();
  }
}
