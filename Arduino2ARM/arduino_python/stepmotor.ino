const int IN1 = 2;
const int IN2 = 3;
const int ENA = 4; //air pump
const int IN3 = 5;
const int IN4 = 6;
const int ENB = 7; //電磁閥
const int limit1 = 9; //限位開關1
const int limit2 = 10; //限位開關2
const int STEP_PIN = 12;
const int DIR_PIN = 13;

//const int EN_PIN = 13;
int steps_per_rev = 200; // 全步進情況下
int total_steps = 0;
bool limit_triggered = false;
unsigned long lastLimitTriggerTime = 0;
const unsigned long debounceDelay = 200;
String input = "";

// M1 控制參數
bool m1_running = false;
int m1_state = 0; // 0: 停止, 1: 充氣
unsigned long m1_last_change = 0;
int m1_cycle_count = 0;

// M2 控制參數
bool m2_started = false;
unsigned long m2_start_time = 0;
int m2_phase = 0; // 0: 未開始, 1: 正轉, 2: 等待, 3: 反轉, 4: 完成
int m2_step_count = 0;
unsigned long m2_last_step_time = 0; // 加入這個變數全域宣告
//int m2_step_delay = 2; // 每 2ms 一步（500us 高 + 500us 低 = 1ms，這樣較保守）

void setup() {
  Serial.begin(9600);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);
  pinMode(STEP_PIN, OUTPUT);
//  pinMode(EN_PIN, OUTPUT);
  pinMode(limit1 , INPUT_PULLUP);
  pinMode(limit2, INPUT_PULLUP);
  delay(1000); // 等待穩定
}

void motor1_start() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, 150);
}

void motor1_stop() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, 0);
}

void step(){
  digitalWrite(STEP_PIN, HIGH); // 把 STEP 腳變成高電位（5V）
  delayMicroseconds(500);       // 等待 500 微秒
  digitalWrite(STEP_PIN, LOW);  // 把 STEP 腳變成低電位（0V）
  delayMicroseconds(500);
}

void motor2_forward() { //步進馬達前進
  digitalWrite(DIR_PIN, HIGH); // 設定方向（HIGH 或 LOW）
  step();
}

void motor2_backward() { //步進馬達後退
  digitalWrite(DIR_PIN, LOW); // 設定方向（HIGH 或 LOW）
  step();
}

void vavle_open() {
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  analogWrite(ENB, 150);
}

void vavle_close() {
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(ENB, 150);
}

void loop() {
  unsigned long now = millis();

  if (Serial.available() && !m1_running && m2_phase == 0) {
    input = Serial.readStringUntil('\n');
    input.trim();
  }

  // === 輸入初始化區段 ===
  if (input != "") {
    if (input == "A") {
      m1_running = true;
      m1_last_change = now;
      m1_state = 1;
      m1_cycle_count = 0;
      m2_step_count = 0;
      m2_started = false;
      m2_phase = 0; 
      total_steps = steps_per_rev * 10;
    } else if (input == "B") {
      m1_running = true;
      m1_last_change = now;
      m1_state = 1;
      m1_cycle_count = 0;
      m2_step_count = 0;
      m2_started = false;
      m2_phase = 0;
      total_steps = steps_per_rev * 25;
    }else if (input == "C") {
      m1_running = true;
      m1_last_change = now;
      m1_state = 1;
      m1_cycle_count = 0;
      m2_step_count = 0;
      m2_started = false;
      m2_phase = 0;
      total_steps = steps_per_rev * 30;
    }else{
      // 吸氣（馬達反轉）
      digitalWrite(IN1, LOW);
      digitalWrite(IN2, LOW);
      total_steps = steps_per_rev * 0;
      m1_running = false;
    }
    input = ""; // 確保不重複執行
  }

  // === 控制馬達1循環 ===
  if (m1_running && m2_phase != 2 && m2_phase != 3 && m2_phase != 4) {
    if (m1_state == 1 && now - m1_last_change >= 2000) {
      motor1_stop();
      m1_state = 0;
      m1_last_change = now;
      m1_cycle_count++;
    } else if (m1_state == 0 && now - m1_last_change >= 3000) {
      motor1_start();
      m1_state = 1;
      m1_last_change = now;
    }
  }

  // === M2 控制流程（M1 執行3次循環後）===
  if (!m2_started && m1_cycle_count >= 4) {
    m2_started = true;
    m2_phase = 1;
    m1_running = false;
    m1_state = 0;
    m1_cycle_count = 0;
  }
  if (m2_phase == 1 && m2_step_count < total_steps){
    motor2_forward();
    m2_step_count++;
  }

  if (m2_phase == 1 && m2_step_count >= total_steps) {
    m2_phase = 2;
    motor1_stop();
    m2_start_time = now;
    m2_step_count = 0;
    vavle_close();
  }

  else if (m2_phase == 2 && now - m2_start_time >= 5000) {
    m2_phase = 3;
    m2_start_time = now;
  }
  if (m2_phase == 3 && m2_step_count < total_steps){
    motor2_backward();
    m2_step_count++;
  }

  else if (m2_phase == 3 && m2_step_count >= total_steps || digitalRead(limit1) == LOW || digitalRead(limit2) == LOW) {
    m2_phase = 4;
    motor1_stop();
    m1_running = false;
    m2_step_count = 0;
  }

  else if (m2_phase == 4) {
    m2_phase = 0;
    m2_started = false;
    m1_running = false;
    m1_state = 0;
    m1_cycle_count = 0;
    vavle_open();
  }

}