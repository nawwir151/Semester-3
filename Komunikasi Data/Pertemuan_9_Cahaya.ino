// Program untuk mengontrol nyala LED dengan input dari nilai LDR
int Led = 10; // deklarasi LED pada pin 10 Arduino
int LDR = A5; // deklarasi LDR pada pin A5 Arduino

void setup() {
    pinMode(Led, OUTPUT); // deklarasi LED sebagai output
}

void loop() {
    int cahaya = analogRead(LDR); // membaca nilai ADC LDR

    // Jika nilai ADC > 800 maka LED menyala
    if (cahaya > 800) {
        digitalWrite(Led, HIGH); // LED menyala
    }
    else {
        digitalWrite(Led, LOW); // LED mati
    }
}