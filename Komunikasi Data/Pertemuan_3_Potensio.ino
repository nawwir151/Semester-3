int potPin = A0; // inisiasi potensio pada pin A0
int ledPin = 9;  // inisiasi LED pada pin 9
int val = 0;     // inisiasi variable val dengan nilai 0

void setup() {
  pinMode(ledPin, OUTPUT); // inisiasi pin LED sebagai output
}

void loop() {
  val = analogRead(potPin); // membaca nilai analog dari pin potensio dan dimasukkan ke variabel val
  digitalWrite(ledPin, HIGH); // menyalakan LED
  delay(val);                 // menunggu sesuai nilai variabel val
  digitalWrite(ledPin, LOW);  // mematikan LED
  delay(val);                 // menunggu sesuai nilai variabel val[cite: 45]
}