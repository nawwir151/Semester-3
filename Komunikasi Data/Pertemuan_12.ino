#include "CTBot.h"

CTBot myBot;

String ssid = "mySSID";       // Ganti dengan nama Wi-Fi
String pass = "myPassword";   // Ganti dengan password Wi-Fi
String token = "myToken";     // Ganti dengan token Telegram Bot

uint8_t led1 = D1;
uint8_t led2 = D2;             // LED onboard ESP8266

void setup() {
    Serial.begin(115200);
    Serial.println("Starting TelegramBot...");

    myBot.wifiConnect(ssid, pass);
    myBot.setTelegramToken(token);

    if (myBot.testConnection())
        Serial.println("\ntestConnection OK");
    else
        Serial.println("\ntestConnection NOK");

    pinMode(led1, OUTPUT);
    pinMode(led2, OUTPUT);

    // LED ESP8266 menggunakan logika terbalik pada contoh modul
    digitalWrite(led1, LOW);
    digitalWrite(led2, LOW);
}

void loop() {
    TBMessage msg;

    if (myBot.getNewMessage(msg)) {
        if (msg.text.equalsIgnoreCase("LED1 Turn on")) {
            digitalWrite(led1, HIGH);
            myBot.sendMessage(msg.sender.id, "LED1 is now ON");
        }
        else if (msg.text.equalsIgnoreCase("LED1 is OFF")) {
            digitalWrite(led1, LOW);
            myBot.sendMessage(msg.sender.id, "LED1 is now OFF");
        }
        else if (msg.text.equalsIgnoreCase("LED2 Turn on")) {
            digitalWrite(led2, HIGH);
            myBot.sendMessage(msg.sender.id, "LED2 is now ON");
        }
        else if (msg.text.equalsIgnoreCase("LED2 is OFF")) {
            digitalWrite(led2, LOW);
            myBot.sendMessage(msg.sender.id, "LED2 is now OFF");
        }
        else {
            String reply = "Welcome " + msg.sender.username +
                           ". Try LED1 Turn on or LED1 is OFF.";
            myBot.sendMessage(msg.sender.id, reply);
        }
    }

    delay(500);
}
