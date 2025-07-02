const int LIMIT1_PIN = 9;    // Limit switch 1
const int LIMIT2_PIN = 10;   // Limit switch 2
const int DIR_PIN = 12;      // Stepper motor DIR
const int STEP_PIN = 13;     // Stepper motor STEP


// === Parameter Constants ===
const int STEPS_PER_REV = 200;      // Steps per revolution for stepper motor
const int MAX_STEPS = 1800;         // Maximum stepper steps (safety protection)

// === State Variables ===
String serialInput = "";            // Serial input command

// Stepper motor state
int stepperPhase = 0;               // 0: Stop  1: Forward  2: Stop  3: Backward
int totalSteps = 0;                 // Target steps
int stepperStepCount = 0;           // Steps taken

void setup() {
  Serial.begin(9600); // Start serial communication
  pinMode(DIR_PIN, OUTPUT);     
  pinMode(STEP_PIN, OUTPUT);
  pinMode(LIMIT1_PIN, INPUT_PULLUP); 
  pinMode(LIMIT2_PIN, INPUT_PULLUP);
  delay(1000); // Delay 1 second after startup
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

void loop() {
  // 1. Immediately stop stepper motor if limit switch is triggered
  if (digitalRead(LIMIT1_PIN) == HIGH || digitalRead(LIMIT2_PIN) == HIGH){
    stepperPhase = 0;
    stepperStepCount = 0;
    Serial.println("Over");
  }
  
  // 2. Read serial command (only when system is idle)
  if (Serial.available() && stepperPhase == 0) {
    serialInput = Serial.readStringUntil('\n');
    serialInput.trim();
  }
  
  // 3. When running, clear serial buffer to avoid misreading
  if (stepperPhase != 0) {
    while (Serial.available()) Serial.read();
  }

  // 4. Process input command and determine steps
  if (serialInput != "") {
    stepperPhase = 1;
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
      stepperPhase = 0;
    }
    serialInput = "";
    
    if (totalSteps >= STEPS_PER_REV * 9) {Serial.println("too many steps!!!");}
  }
  
  // 5. Stepper motor forward
  if (stepperPhase == 1) {
    stepperForward();
    stepperStepCount++;
  }

  // 6. After forward, enter exhaust wait
  if (stepperPhase == 1 && stepperStepCount >= totalSteps) {
    stepperPhase = 2;
    stepperStepCount = 0;
    stepperPhase = 3;
  }
  
  // 7. Stepper motor backward
  if (stepperPhase == 3) {
    stepperBackward();
    stepperStepCount++;
  }

  // 8. After backward or limit triggered, end process
  if (stepperPhase == 3 && stepperStepCount >= totalSteps) {
    stepperPhase = 0;
    stepperStepCount = 0;
    Serial.println("Over");
  } 
}
