#include <Servo.h>

Servo myServo;
const int trigPin = 12;
const int echoPin = 11;
const int servoPin = 6;
const int ledPins[6] = {8, 7, 5, 4, 3, 2}; // LED 1 hingga LED 6

long duration;
int distance;

void setup() {
  myServo.attach(servoPin);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  for (int i = 0; i < 6; i++) {
    pinMode(ledPins[i], OUTPUT);
  }
}

void loop() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  distance = duration * 0.034 / 2;

  if (distance <= 3) {
    setLeds(LOW, HIGH, HIGH, HIGH, HIGH, HIGH);
    myServo.write(30);
  } else if (distance <= 6) {
    setLeds(LOW, LOW, HIGH, HIGH, HIGH, HIGH);
    myServo.write(60);
  } else if (distance <= 9) {
    setLeds(LOW, LOW, LOW, HIGH, HIGH, HIGH);
    myServo.write(90);
  } else if (distance <= 12) {
    setLeds(LOW, LOW, LOW, LOW, HIGH, HIGH);
    myServo.write(120);
  } else if (distance <= 15) {
    setLeds(LOW, LOW, LOW, LOW, LOW, HIGH);
    myServo.write(150);
  } else if (distance <= 18) {
    setLeds(LOW, LOW, LOW, LOW, LOW, LOW);
    myServo.write(180);
  } else {
    setLeds(HIGH, HIGH, HIGH, HIGH, HIGH, HIGH);
    myServo.write(0);
  }
  delay(100);
}

void setLeds(int l1, int l2, int l3, int l4, int l5, int l6) {
  digitalWrite(ledPins[0], l1);
  digitalWrite(ledPins[1], l2);
  digitalWrite(ledPins[2], l3);
  digitalWrite(ledPins[3], l4);
  digitalWrite(ledPins[4], l5);
  digitalWrite(ledPins[5], l6);
}