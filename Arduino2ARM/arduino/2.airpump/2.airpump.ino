// === Pin Definitions ===
const int AIRPUMP_IN2 = 5;   // Air pump motor IN2
const int AIRPUMP_IN1 = 6;   // Air pump motor IN1
const int AIRPUMP_ENA = 7;   // Air pump motor ENA (PWM)
const int AIRPUMP_PWM = 130; // Air pump PWM speed

// Air pump state
int airpumpPhase = 0;        // 0: Initial state  1: Inflating  2: Stopped

void setup() {
  pinMode(AIRPUMP_IN1, OUTPUT); 
  pinMode(AIRPUMP_IN2, OUTPUT); 
  pinMode(AIRPUMP_ENA, OUTPUT);
  delay(1000);
}

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

void loop() {
  // 1. (Safety protection, do not modify!!)
  if (AIRPUMP_PWM <= 140 && airpumpPhase == 0){airpumpPhase = 1;}
  else if (AIRPUMP_PWM > 140) {Serial.println("airpump too fast!!!");}

  // 2. (Air pump inflation)
  if (airpumpPhase == 1){
    airpumpStart();  // Start air pump
    delay(1500);     // Inflate for 1.5 seconds
    airpumpStop();   // Stop air pump
    delay(1000);     // Wait for 1.0 second
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
