#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Keypad.h>

// 1. Konfigurasi LCD I2C
// Alamat I2C umum biasanya 0x27 atau 0x3F, dengan ukuran 16 kolom x 2 baris
LiquidCrystal_I2C lcd(0x27, 16, 2);

// 2. Konfigurasi Keypad 4x4
const byte ROWS = 4;
const byte COLS = 4;

// Layout tombol pada Keypad 4x4
char hexaKeys[ROWS][COLS] = {
  {'1', '2', '3', 'A'},
  {'4', '5', '6', 'B'},
  {'7', '8', '9', 'C'},
  {'*', '0', '#', 'D'}
};

// Sambungan pin baris dan kolom ke Arduino UNO
byte rowPins[ROWS] = {13, A2, 11, 10}; // R1, R2, R3, R4
byte colPins[COLS] = {9, 8, 7, 6};     // C1, C2, C3, C4

// Inisialisasi objek Keypad
Keypad customKeypad = Keypad(makeKeymap(hexaKeys), rowPins, colPins, ROWS, COLS);

void setup() {
  // Inisialisasi Serial Monitor
  Serial.begin(9600);
  Serial.println("--- Praktikum Keypad 4x4 & LCD I2C ---");

  // Inisialisasi LCD I2C
  lcd.init();
  lcd.backlight(); // Nyalakan lampu latar (backlight) LCD

  // Tampilan Selamat Datang
  lcd.setCursor(0, 0);
  lcd.print(" Keypad 4x4 I2C");
  lcd.setCursor(0, 1);
  lcd.print("Tekan Tombol...");

  delay(1500);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Tombol Ditekan:");
}

void loop() {
  // Membaca input tombol dari keypad
  char customKey = customKeypad.getKey();

  // Jika ada tombol yang ditekan
  if (customKey) {
    // 1. Tampilkan ke Serial Monitor
    Serial.print("Karakter Ditekan: ");
    Serial.println(customKey);

    // 2. Tampilkan ke LCD I2C (Baris ke-2)
    lcd.setCursor(0, 1);
    lcd.print("                "); // Bersihkan teks baris kedua
    lcd.setCursor(0, 1);
    lcd.print("Key: ");
    lcd.print(customKey);
  }
}