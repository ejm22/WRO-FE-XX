#include <Arduino.h>
#include <FlexyStepper.h>
#include <Servo.h>

const int dirPin = 2;
const int stepPin = 9;
const int enablePin = 10;
const int anglePin = 11;
int angle = 88; // initial angle for the servo
int speed = 0; // initial speed for the stepper
long int targetPosition = -10000000; // target position for the stepper

String inputString = ""; // a string to hold incoming data
bool stringComplete = false; // whether the string is complete

Servo servo;
FlexyStepper stepper;

void processSerialCommand();

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
    processSerialCommand();
}

void processSerialCommand()
{
    if (Serial.available()) {
        char inChar = (char)Serial.read();
        if (inChar == '.') {
            stringComplete = true;
        } else inputString += inChar;
    }

    if (stringComplete) {
        int commaIndex = inputString.indexOf(',');
        if (commaIndex > 0) {
            angle = inputString.substring(0, commaIndex).toInt();
            if (angle < 48 || angle > 138) {
                Serial.println("Angle must be between 48 and 138.");
                inputString = ""; // clear the string for the next command
                stringComplete = false; // reset the flag
                return;
            }
            speed = inputString.substring(commaIndex + 1).toInt();
            if (speed < -6000 || speed > 6000) {
                Serial.println("Speed must be between -6000 and 6000.");
                inputString = ""; // clear the string for the next command
                stringComplete = false; // reset the flag
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
        stringComplete = false; // reset the flag
    }
}


/*#include <Arduino.h>

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
  */