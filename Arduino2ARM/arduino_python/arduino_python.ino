// === Pin 定義 ===
const int IN1 = 2, IN2 = 3, ENA = 4;   // 控制空氣泵（馬達1）的方向與速度（ENA 是 PWM 腳）
const int IN3 = 5, IN4 = 6, ENB = 7;   // 控制電磁閥開關（ENB 是 PWM 腳）
const int limit1 = 9, limit2 = 10;     // 兩個限位開關（輸入，用於安全終止）
const int STEP_PIN = 12, DIR_PIN = 13; // 步進馬達控制腳位（步進、方向）

// === 常數與變數 ===
const int steps_per_rev = 200;    // 步進馬達每轉一圈需要 200 步
int total_steps = 0;              // 儲存目前要轉動的總步數
String input = "";                // 儲存從序列埠接收的指令字串
// 打氣馬達參數（空氣泵）
bool m1_running = false;          // 表示空氣泵是否正在運行
int m1_phase = 0;                 // 空氣泵階段：0 停止、1 充氣
int m1_cycle_count = 0;           // 空氣泵充氣/停止的循環次數
unsigned long m1_last_change = 0; // 記錄空氣泵狀態改變的時間
// 步進馬達參數
bool m2_running = false;          // 步進馬達是否正在運行
int m2_phase = 0;                 // 步進馬達狀態：0 停止、1 正轉、2 等待、3 反轉
int m2_step_count = 0;            // 目前已走的步數
unsigned long m2_start_time = 0;  // 記錄開始等待或反轉的起始時間

void setup() {
  Serial.begin(9600);                                               // 啟動序列通訊，設定鮑率為 9600
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT); pinMode(ENA, OUTPUT); // 設定空氣泵控制腳為輸出
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT); pinMode(ENB, OUTPUT); // 設定電磁閥控制腳為輸出
  pinMode(DIR_PIN, OUTPUT); pinMode(STEP_PIN, OUTPUT);              // 設定步進馬達控制腳為輸出
  pinMode(limit1, INPUT_PULLUP); pinMode(limit2, INPUT_PULLUP);     // 設定限位開關為輸入（上拉）
  delay(1000);                                                      // 啟動後延遲 1 秒，確保穩定
}
// 啟動空氣泵
void motor1_start() {digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW); analogWrite(ENA, 150); } // 設定方向與速度（PWM）
// 停止空氣泵
void motor1_stop() {digitalWrite(IN1, LOW); digitalWrite(IN2, LOW); analogWrite(ENA, 0); }     // 關閉所有輸出
// 步進馬達速度控制
void step_V() {delayMicroseconds(1000); }// 高電位 5ms（控制速度）
// 步進馬達走一步
void step() {
  digitalWrite(STEP_PIN, HIGH); step_V(); // 高電位 5ms（控制速度）
  digitalWrite(STEP_PIN, LOW); step_V();  // 低電位 5ms（控制速度）
}
// 步進馬達正轉
void motor2_forward() {digitalWrite(DIR_PIN, HIGH); step(); } // 設定方向為 HIGH，並走一步
// 步進馬達反轉
void motor2_backward() {digitalWrite(DIR_PIN, LOW); step(); } // 設定方向為 LOW，並走一步
// 打開電磁閥（封閉狀態）
void vavle_open() {digitalWrite(IN3, LOW); digitalWrite(IN4, LOW); analogWrite(ENB, 150); }   // 保持電磁閥閉合
// 關閉電磁閥（排氣狀態）
void vavle_close() {digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW); analogWrite(ENB, 150); } // 排氣方向

void loop() {
  unsigned long now = millis(); // 取得目前時間（毫秒）

  // 當有輸入資料，且系統沒在運行，則讀取輸入
  if (Serial.available() && !m1_running && m2_phase == 0) {
    input = Serial.readStringUntil('\n'); // 讀取一行輸入直到換行
    input.trim();                         // 去除空白字元
  }

  // 如果正在執行，清空序列緩衝區避免誤讀
  if (m1_running || m2_phase != 0) {while (Serial.available()) Serial.read(); } // 清空所有輸入

  // === 處理輸入指令 ===
  if (input != "") {
    if (input == "A") { total_steps = steps_per_rev * 10; }      // A 指令：轉 10 圈
    else if (input == "B") { total_steps = steps_per_rev * 20; } // B 指令：轉 20 圈
    else if (input == "C") { total_steps = steps_per_rev * 60; } // C 指令：轉 30 圈

    if ( total_steps > 0 && total_steps < 10000 ) {        // 如果總步數有效，初始化流程
      m1_running = true;          // 啟動空氣泵
      m1_last_change = now;       // 記錄當前時間
      m1_phase = 1;               // 空氣泵進入充氣階段
      m1_cycle_count = 0;         // 重設循環計數
      m2_step_count = 0;          // 重設步數
      m2_running = false;         // 尚未開始執行 M2
      m2_phase = 0;               // M2 初始化為停止
    }
    if (total_steps > steps_per_rev * 50){Serial.println("too many steps");} // 防止碰撞
    input = "";                   // 清空輸入，避免重複觸發
  }

  // === 控制空氣泵循環 ===
  if (m1_running && m2_phase != 2 && m2_phase != 3 && m2_phase != 4) {
    if (m1_phase == 1 && now - m1_last_change >= 2000) {
      motor1_stop();              // 每次充氣 2 秒後停止
      m1_phase = 0;               // 切換為停止狀態
      m1_last_change = now;       // 記錄時間
      m1_cycle_count++;           // 累計循環次數
    } else if (m1_phase == 0 && now - m1_last_change >= 3000) {
      motor1_start();             // 停止 3 秒後重新啟動充氣
      m1_phase = 1;
      m1_last_change = now;
    }
  }

  // === 步進馬達 M2 控制流程 ===
  if (!m2_running && m1_cycle_count >= 4) {
    m2_running = true;           // 開始執行步進馬達
    m2_phase = 1;                // 進入正轉階段
    m1_running = false;          // 關閉空氣泵
    m1_phase = 0;
    m1_cycle_count = 0;
  }
  // 正轉階段：執行指定步數
  if (m2_phase == 1 && m2_step_count < total_steps) {
    motor2_forward();            // 正轉一步
    m2_step_count++;             // 累加步數
  }
  // 正轉完成 → 進入等待階段（關閥、等待排氣）
  if (m2_phase == 1 && m2_step_count >= total_steps) {
    m2_phase = 2;                // 進入等待
    motor1_stop();               // 關閉空氣泵（安全保險）
    m2_start_time = now;         // 記錄等待開始時間
    m2_step_count = 0;           // 步數重設，用於反轉
    vavle_close();               // 排氣
  }
  // 等待排氣結束，進入反轉階段
  else if (m2_phase == 2 && now - m2_start_time >= 3000) {
    m2_phase = 3;
    m2_start_time = now;
  }
  // 反轉階段：執行與正轉相同步數的反轉
  if (m2_phase == 3 && m2_step_count < total_steps) {
    motor2_backward();           // 反轉一步
    m2_step_count++;
  }
  // 任一條件達成：反轉完成 or 碰到限位 → 結束整個流程
  else if (m2_phase == 3 && m2_step_count >= total_steps || digitalRead(limit1) == LOW || digitalRead(limit2) == LOW) {
    motor1_stop();               // 關閉空氣泵
    m1_running = false;
    m1_phase = 0;
    m1_cycle_count = 0;
    m2_running = false;
    m2_phase = 0;
    m2_step_count = 0;
    vavle_open();                // 關閉排氣（封閉電磁閥）
  }
}
