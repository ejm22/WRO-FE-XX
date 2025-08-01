/// @file main.cpp
/// @brief Main file for controlling the stepper motor and servo
/// @author Michael Bruneau
/// @date 24-07-2025
/// @version 2.0 : Added voltage measurement and improved command handling


#include <Arduino.h>
#include <FlexyStepper.h>
#include <Servo.h>
#include "utils/voltage_utils.h"
#include "classes/serial_reciever.h"

const int DIR_PIN = 2;       // Pin for stepper motor direction
const int STEP_PIN = 9;      // Pin for stepper motor control
const int ENABLE_PIN = 10;   // Pin for enabling/disabling the stepper motor
const int ANGLE_PIN = 11;    // Pin for servo control
const int ACCELERATION = 2000; // Acceleration for the stepper motor

// Voltage divider for battery voltage measurement
const int R1 = 20000;       // Resistor R1 in ohms
const int R2 = 10000;       // Resistor R2 in ohms

int angle = 88;             // initial angle for the servo
int speed = 0;              // initial speed for the stepper
long int targetPosition = -10000000;    // target position for the stepper

String inputString = "";    // a string to hold incoming data

Servo servo;                // Create a Servo object
FlexyStepper stepper;       // Create a FlexyStepper object
SerialReceiver serialReceiver(servo, stepper, angle, speed, targetPosition);

void setup() {
    Serial.begin(115200);
    servo.attach(ANGLE_PIN);

    stepper.connectToPins(STEP_PIN, DIR_PIN);
    stepper.setCurrentPositionInSteps(0);
    stepper.setTargetPositionInSteps(0);
    stepper.setAccelerationInStepsPerSecondPerSecond(ACCELERATION);
    stepper.setSpeedInStepsPerSecond(speed);
    pinMode(ENABLE_PIN, OUTPUT);
    digitalWrite(ENABLE_PIN, LOW);
}

void loop() {
    if (speed == 0 && abs(stepper.getCurrentVelocityInStepsPerSecond()) < 100) {
      digitalWrite(ENABLE_PIN, HIGH); // Disable stepper when speed is 0
    } else digitalWrite(ENABLE_PIN, LOW); // Enable stepper when speed is not 0
    stepper.processMovement();
    serialReceiver.processSerial();
}