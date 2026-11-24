const int PinLED = 13;
const int PinSUARA = A2;
const int AmbangNilai = 200;

void setup() {
    Serial.begin(9600);
    pinMode(PinLED, OUTPUT);
    pinMode(PinSUARA, INPUT);
}

void loop() {
    int SensorSuara = analogRead(PinSUARA);

    if (SensorSuara > AmbangNilai) {
        digitalWrite(PinLED, HIGH);
        delay(500);
    }
    else {
        digitalWrite(PinLED, LOW);
    }
}