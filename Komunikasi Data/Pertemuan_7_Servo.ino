#include <Servo.h> // Mengimport library Servo

// Mendeklarasikan objek Servo
Servo myServo;

// Mendeklarasikan pin
const int ledPin = 7;    // Pin LED
const int servoPin = 11; // Pin Servo

void setup() {
  // Inisialisasi pin LED sebagai OUTPUT
  pinMode(ledPin, OUTPUT);
  // Menyambungkan objek servo ke pin 11
  myServo.attach(servoPin);
}

void loop() {
  // Menggerakkan servo dari 0° ke 180°
  for (int pos = 0; pos <= 180; pos++) {
    myServo.write(pos);           // Menetapkan posisi servo
    digitalWrite(ledPin, HIGH);   // Menyalakan LED
    delay(15);                    // Tunggu 15ms agar servo dapat mencapai posisi
    digitalWrite(ledPin, LOW);    // Mematikan LED
    delay(15);                    // Tunggu 15ms sebelum menggerakkan servo ke posisi berikutnya
  }

  // Menggerakkan servo dari 180° ke 0°
  for (int pos = 180; pos >= 0; pos--) {
    myServo.write(pos);           // Menetapkan posisi servo
    digitalWrite(ledPin, HIGH);   // Menyalakan LED
    delay(15);                    // Tunggu 15ms agar servo dapat mencapai posisi
    digitalWrite(ledPin, LOW);    // Mematikan LED
    delay(15);                    // Tunggu 15ms sebelum menggerakkan servo ke posisi berikutnya[cite: 7, 8]
  }
}