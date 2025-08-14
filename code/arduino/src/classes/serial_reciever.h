#ifndef SERIAL_RECEIVER_H
#define SERIAL_RECEIVER_H

#include <Arduino.h>
#include <FlexyStepper.h>
#include <Servo.h>
#include "utils/voltage_utils.h"

const int DEFAULT_ANGLE = 88;             // initial angle for the servo
const int DEFAULT_SPEED = 0;              // initial speed for the stepper
const long int DEFAULT_TARGET_POSITION = -10000000;    // target position for the stepper

const int ANGLE_MIN = 48;    // Minimum angle for the servo
const int ANGLE_MAX = 138;   // Maximum angle for the servo

const int SPEED_MIN = 300;   // Maximum negative speed for the stepper
const int SPEED_MAX = 6000;  // Maximum speed for the stepper

class SerialReceiver {
private:
    Servo &servo;
    FlexyStepper &stepper;
    String inputString;
    int &angle;
    int &speed;
    long int &targetPosition;

public:
    SerialReceiver(Servo &servoRef, FlexyStepper &stepperRef, int &angleRef, int &speedRef, long int &targetPositionRef);
    void processSerial();
    void decryptMovementOrder();
    bool waitingForTarget = false; // Flag to indicate if waiting for target position
};

#endif