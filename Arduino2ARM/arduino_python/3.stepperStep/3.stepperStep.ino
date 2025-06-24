const int LIMIT1_PIN = 9;    // 限位開關1
const int LIMIT2_PIN = 10;   // 限位開關2
const int DIR_PIN = 12;      // 步進馬達 DIR
const int STEP_PIN = 13;     // 步進馬達 STEP


// === 參數常數 ===
const int STEPS_PER_REV = 200;      // 步進馬達一圈步數
const int MAX_STEPS = 1800;         // 步進馬達最大步數（安全保護）

// === 狀態變數 ===
String serialInput = "";            // 序列埠輸入指令

// 步進馬達狀態
int stepperPhase = 0;               // 0: 停止  1: 正轉  2: 停止  3: 反轉
int totalSteps = 0;                 // 目標步數
int stepperStepCount = 0;           // 已走步數

void setup() {
  Serial.begin(9600); // 啟動序列通訊
  pinMode(DIR_PIN, OUTPUT);     
  pinMode(STEP_PIN, OUTPUT);
  pinMode(LIMIT1_PIN, INPUT_PULLUP); 
  pinMode(LIMIT2_PIN, INPUT_PULLUP);
  delay(1000); // 啟動後延遲 1 秒
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

void loop() {
  // 1. 讀取序列埠指令（只在系統閒置時）
  if (Serial.available() && stepperPhase == 0) {
    serialInput = Serial.readStringUntil('\n');
    serialInput.trim();
  }
  
  // 2. 執行中時清空序列緩衝區，避免誤讀
  if (stepperPhase != 0) {
    while (Serial.available()) Serial.read();
  }

  // 3. 處理輸入指令，決定步數
  if (serialInput != "") {
    stepperPhase = 1;
    if (serialInput == "A" || serialInput == "D") {
      totalSteps = STEPS_PER_REV * 3; // 轉 3 圈
      Serial.println("Go to first box");
    } else if (serialInput == "B" || serialInput == "E") {
      totalSteps = STEPS_PER_REV * 5; // 轉 5 圈
      Serial.println("Go to second box");
    } else if (serialInput == "C" || serialInput == "F") {
      totalSteps = STEPS_PER_REV * 7; // 轉 7 圈
      Serial.println("Go to last box");
    } else {
      Serial.println("Nothing");
      stepperPhase = 0;
    }
    serialInput = "";

    // 4. 安全保護
    if (totalSteps >= STEPS_PER_REV * 9) {Serial.println("too many steps,太多圈了!!!");}
  }
  
  // 5. 步進馬達正轉
  if (stepperPhase == 1) {
    stepperForward();
    stepperStepCount++;
  }

  // 6. 正轉完成，進入排氣等待
  if (stepperPhase == 1 && stepperStepCount >= totalSteps) {
    stepperPhase = 2;
    stepperStepCount = 0;
    stepperPhase = 3;
  }
  
  // 7. 步進馬達反轉
  if (stepperPhase == 3) {
    stepperBackward();
    stepperStepCount++;
  }

  // 8. 反轉完成或碰到限位，結束流程
  if (stepperPhase == 3 && stepperStepCount >= totalSteps || digitalRead(LIMIT1_PIN) == LOW || digitalRead(LIMIT2_PIN) == LOW) {
    Serial.println("Over");
    stepperPhase = 0;
    stepperStepCount = 0;
  } 
}
