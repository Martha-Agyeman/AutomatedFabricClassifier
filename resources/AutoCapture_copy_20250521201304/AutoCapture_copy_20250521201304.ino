// Define pins for HC-SR04
const int trigPin = 5;
const int echoPin = 18;

// Distance threshold (cm) and duration (ms)
const int distanceThreshold = 15;
const unsigned long durationThreshold = 7000; // 7 seconds

// Detection variables
unsigned long detectionStartTime = 0;
bool objectDetected = false;

void setup() {
  Serial.begin(9600);
  while (!Serial); 
  
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  
  Serial.println("ESP32 Ultrasonic Sensor Ready");
}

void loop() {
  // Measure distance
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  long duration = pulseIn(echoPin, HIGH);
  int distance = duration * 0.034 / 2;

  // Debug output (optional)
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  // Detection logic
  if (distance > 0 && distance < distanceThreshold) {
    if (!objectDetected) {
      detectionStartTime = millis();
      objectDetected = true;
      Serial.println("Object detected - starting timer");
    }
    else if (millis() - detectionStartTime >= durationThreshold) {
      Serial.println("TAKE_PICTURE"); 
      objectDetected = false;
      delay(3000); 
    }
  }
  else {
    if (objectDetected) {
      Serial.println("Object removed - resetting timer");
    }
    objectDetected = false;
  }

  delay(100); // Main loop delay
}