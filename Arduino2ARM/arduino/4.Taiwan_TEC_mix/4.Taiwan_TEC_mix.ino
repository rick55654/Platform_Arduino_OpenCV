// Taiwan_TEC.ino
// =============================
// Arduino control example for air pump, stepper motor, and solenoid valve
// =============================
// This program demonstrates how to control a pneumatic and stepper motor system via commands,
// with detailed comments for each step.
//
// [Hardware Connection]
// IN1, IN2, ENA: Control air pump motor (M1)
// IN3, IN4, ENB: Control solenoid valve
// limit1, limit2: Two limit switches (safety protection)
// STEP_PIN, DIR_PIN: Stepper motor control pins
//
// [Command Description]
// Send commands A~F via serial port to control the number of motor rotations
//
// =============================

// === Pin Definitions ===
const int VALVE_ENB = 2;     // Solenoid valve ENB (PWM)
const int VALVE_IN4 = 3;     // Solenoid valve IN4
const int VALVE_IN3 = 4;     // Solenoid valve IN3
const int AIRPUMP_IN2 = 5;   // Air pump motor IN2
const int AIRPUMP_IN1 = 6;   // Air pump motor IN1
const int AIRPUMP_ENA = 7;   // Air pump motor ENA (PWM)
const int LIMIT1_PIN = 9;    // Limit switch 1
const int LIMIT2_PIN = 10;   // Limit switch 2
const int DIR_PIN = 12;      // Stepper motor DIR
const int STEP_PIN = 13;     // Stepper motor STEP

// === Parameter Constants ===
const int STEPS_PER_REV = 200;      // Steps per revolution for stepper motor
const int AIRPUMP_PWM = 130;        // Air pump PWM speed
const int VALVE_PWM = 255;          // Solenoid valve PWM speed
const int MAX_STEPS = 1800;         // Maximum stepper steps (safety protection)

// === State Variables ===
String serialInput = "";            // Serial input command

// Air pump state
int airpumpPhase = 0;               // 0: Waiting for command  1: Inflating  2: All stopped

// Stepper motor state
int stepperPhase = 0;               // 0: Stop  1: Forward  2: Stop  3: Backward
int totalSteps = 0;                 // Target steps
int stepperStepCount = 0;           // Steps taken

// =============================
// Initialization
// =============================
void setup() {
  Serial.begin(9600); // Start serial communication
  // Set all pin modes
  pinMode(AIRPUMP_IN1, OUTPUT); pinMode(AIRPUMP_IN2, OUTPUT); pinMode(AIRPUMP_ENA, OUTPUT);
  pinMode(VALVE_IN3, OUTPUT);   pinMode(VALVE_IN4, OUTPUT);   pinMode(VALVE_ENB, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);     pinMode(STEP_PIN, OUTPUT);
  pinMode(LIMIT1_PIN, INPUT_PULLUP); pinMode(LIMIT2_PIN, INPUT_PULLUP);
  delay(1000); // Delay 1 second after startup
}

// =============================
// Control Functions
// =============================
// Start air pump
void airpumpStart() {
  digitalWrite(AIRPUMP_IN1, HIGH);
  digitalWrite(AIRPUMP_IN2, LOW);
  analogWrite(AIRPUMP_ENA, AIRPUMP_PWM);
}
// Stop air pump
void airpumpStop() {
  digitalWrite(AIRPUMP_IN1, LOW);
  digitalWrite(AIRPUMP_IN2, LOW);
  analogWrite(AIRPUMP_ENA, 0);
}
// Stepper motor single step (speed control)
void stepperStep() {
  digitalWrite(STEP_PIN, HIGH);
  delayMicroseconds(500); // Control speed
  digitalWrite(STEP_PIN, LOW);
  delayMicroseconds(500);
}
// Stepper motor forward one step
void stepperForward() {
  digitalWrite(DIR_PIN, HIGH);
  stepperStep();
}
// Stepper motor backward one step
void stepperBackward() {
  digitalWrite(DIR_PIN, LOW);
  stepperStep();
}
// Solenoid valve closed (close exhaust)
void valveCloseExhaust() {
  digitalWrite(VALVE_IN3, LOW);
  digitalWrite(VALVE_IN4, LOW);
  analogWrite(VALVE_ENB, 0);
}
// Solenoid valve open (open exhaust)
void valveOpenExhaust() {
  digitalWrite(VALVE_IN3, LOW);
  digitalWrite(VALVE_IN4, HIGH);
  analogWrite(VALVE_ENB, VALVE_PWM);
}

// =============================
// Main loop
// =============================
void loop() {
  // 0. If limit switch is triggered, end process
  if (digitalRead(LIMIT1_PIN) == LOW || digitalRead(LIMIT2_PIN) == LOW) {
    airpumpPhase = 0;
    stepperPhase = 0;
    stepperStepCount = 0;
    valveOpenExhaust();
    delay(2000);
    valveCloseExhaust();
    return;
  }

  // 1. Read serial command (only when system is idle)
  if (Serial.available() && airpumpPhase == 0) {
    serialInput = Serial.readStringUntil('\n');
    serialInput.trim();
  }
  // 2. When running, clear serial buffer to avoid misreading
  if (airpumpPhase != 0) {
    while (Serial.available()) Serial.read();
  }

  // 3. Process input command and determine steps
  if (serialInput != "") {
    airpumpPhase = 1;
    if (serialInput == "A" || serialInput == "D") {
      totalSteps = STEPS_PER_REV * 3; // Rotate 3 turns
      Serial.println("Go to first box");
    } else if (serialInput == "B" || serialInput == "E") {
      totalSteps = STEPS_PER_REV * 5; // Rotate 5 turns
      Serial.println("Go to second box");
    } else if (serialInput == "C" || serialInput == "F") {
      totalSteps = STEPS_PER_REV * 7; // Rotate 7 turns
      Serial.println("Go to last box");
    } else {
      Serial.println("Nothing");
    }

    // 4. Safety protection
    if (totalSteps >= STEPS_PER_REV * 9) {Serial.println("too many steps!!!");}
    if (AIRPUMP_PWM >= 140) {Serial.println("airpump too fast!!!");}

    serialInput = "";
  }

  // 5. Air pump control
  if (airpumpPhase == 1 && totalSteps > 0 && totalSteps < MAX_STEPS && AIRPUMP_PWM < 140) {
    delay(5000);
    airpumpStart();
    delay(1500); // inflate for 1.5 seconds
    airpumpStop();
    delay(500);
    airpumpPhase = 2;
    stepperPhase = 1;
  }

  // 6. Stepper motor forward
  if (stepperPhase == 1) {
    stepperForward();
    stepperStepCount++;
  }

  // 7. After forward, enter exhaust wait
  if (stepperPhase == 1 && stepperStepCount >= totalSteps) {
    stepperPhase = 2;
    delay(1000); // For demonstration: observe
    valveOpenExhaust();
    delay(1000);
    stepperStepCount = 0;
    stepperPhase = 3;
  }
  
  // 8. Stepper motor backward
  if (stepperPhase == 3) {
    stepperBackward();
    stepperStepCount++;
  }

  // 9. After backward, end process
  if (stepperPhase == 3 && stepperStepCount >= totalSteps) {
    Serial.println("Over");
    airpumpPhase = 0;
    stepperPhase = 0;
    stepperStepCount = 0;
    valveOpenExhaust();
    delay(2000);
    valveCloseExhaust();
  }
}
