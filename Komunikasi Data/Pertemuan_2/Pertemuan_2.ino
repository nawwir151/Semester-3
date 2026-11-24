void setup() {
  Serial.begin(9600); // set baud rate
  while (!Serial) {
    // Menunggu port serial terhubung
  }
}

void loop() {
  Serial.println("A"); //[cite: 48]
}