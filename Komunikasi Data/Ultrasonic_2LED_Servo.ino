#include <Servo.h>

Servo myServo;
const int servoPin = 7;
const int trigPin = 8;
const int echoPin = 9;
const int ledMerah = 12;
const int ledHijau = 13;

long duration;
int distance;

void setup() {
  myServo.attach(servoPin);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(ledMerah, OUTPUT);
  pinMode(ledHijau, OUTPUT);
  myServo.write(0);
}

void loop() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  distance = duration * 0.034 / 2;

  if (distance <= 15) { // Objek jarak dekat (misal batas 15 cm)
    digitalWrite(ledMerah, HIGH);
    digitalWrite(ledHijau, LOW);
    myServo.write(180);
  } else {              // Objek jarak jauh
    digitalWrite(ledMerah, LOW);
    digitalWrite(ledHijau, HIGH);
    myServo.write(0);
  }
  delay(100);
}