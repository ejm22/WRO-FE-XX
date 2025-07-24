/// @file main.cpp
/// @brief Main file for controlling the stepper motor and servo
/// @author Michael Bruneau
/// @date 24-07-2025
/// @version 2.0 : Added voltage measurement and improved command handling


#include <Arduino.h>
#include <FlexyStepper.h>
#include <Servo.h>

const int dirPin = 2;       // Pin for stepper motor direction
const int stepPin = 9;      // Pin for stepper motor control
const int enablePin = 10;   // Pin for enabling/disabling the stepper motor
const int anglePin = 11;    // Pin for servo control
const int voltagePin = A5;  // Pin for battery voltage measurement

const int angleMin = 48;    // Minimum angle for the servo
const int angleMax = 138;   // Maximum angle for the servo
const int speedMin = 300;   // Maximum negative speed for the stepper
const int speedMax = 6000;  // Maximum speed for the stepper

// Voltage divider for battery voltage measurement
const int R1 = 20000;       // Resistor R1 in ohms
const int R2 = 10000;       // Resistor R2 in ohms

int angle = 88;             // initial angle for the servo
int speed = 0;              // initial speed for the stepper
long int targetPosition = -10000000;    // target position for the stepper

String inputString = "";    // a string to hold incoming data

Servo servo;                // Create a Servo object
FlexyStepper stepper;       // Create a FlexyStepper object

void processSerial();
void showVoltage();
void decryptOrder();

void setup() {
    Serial.begin(115200);
    servo.attach(anglePin);

    stepper.connectToPins(stepPin, dirPin);
    stepper.setCurrentPositionInSteps(0);
    stepper.setTargetPositionInSteps(0);
    stepper.setAccelerationInStepsPerSecondPerSecond(4000);
    stepper.setSpeedInStepsPerSecond(speed);
    pinMode(enablePin, OUTPUT);
    digitalWrite(enablePin, LOW);
}

void loop() {
    if (speed == 0 && abs(stepper.getCurrentVelocityInStepsPerSecond()) < 100) {
      digitalWrite(enablePin, HIGH); // Disable stepper when speed is 0
    } else digitalWrite(enablePin, LOW); // Enable stepper when speed is not 0
    stepper.processMovement();
    processSerial();
}

void processSerial() {
    if (Serial.available()) {
        char inChar = (char)Serial.read();
        if (inChar == 'V' || 'v' == inChar) {
          showVoltage();
          return;
        }
        if (inChar == '.') {
            decryptOrder();
        } else inputString += inChar;
    }
}

void showVoltage() {
    float vA0 = analogRead(A5) * (5.0 / 1023.0);
    float vBattery = vA0 * 3.0; // Because of the voltage divider
    Serial.println("Battery voltage: " + String(vBattery, 1));
}

void decryptOrder() {
    int commaIndex = inputString.indexOf(',');
    if (commaIndex > 0) {
        angle = inputString.substring(0, commaIndex).toInt();
        if (angle < angleMin || angle > angleMax) {
            Serial.println("Angle must be between 48 and 138.");
            inputString = ""; // clear the string for the next command
            return;
        }
            speed = inputString.substring(commaIndex + 1).toInt();
            if (abs(speed) > speedMax) {
                Serial.println("Absolute speed must be between 300 and 6000.");
                inputString = ""; // clear the string for the next command
                return;
            }
            if (speed < 0) {
              stepper.setTargetPositionInSteps(-targetPosition);
              speed = abs(speed); // Reverse direction if speed is negative
            } else stepper.setTargetPositionInSteps(targetPosition);

            servo.write(angle);
            stepper.setSpeedInStepsPerSecond(speed);
    }   else Serial.println("Invalid input format. Use 'angle,speed.'");
    inputString = ""; // clear the string for the next command
}