#include <Arduino.h>

// Test code to trigger the led based on Pi input

enum LED_STATE {
  LED_ON = 1,
  LED_OFF = 0,
};

void setup() {
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    char receivedChar = Serial.read();
    digitalWrite(LED_BUILTIN, receivedChar == '1' ? LED_ON : LED_OFF);
  }
}