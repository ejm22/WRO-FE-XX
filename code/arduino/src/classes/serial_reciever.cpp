#include "serial_reciever.h"

SerialReceiver::SerialReceiver(Servo &servoRef, FlexyStepper &stepperRef, int &angleRef, int &speedRef, long int &targetPositionRef)
 : servo(servoRef), stepper(stepperRef), angle(angleRef), speed(speedRef), targetPosition(targetPositionRef) {
    inputString = "";
}

void SerialReceiver::processSerial() {
    while (Serial.available()) {
        char inChar = (char)Serial.read();
        switch (inChar) {
            case 'v':
            case 'V':
                VoltageUtils::showVoltage();
                break;

            case '.':
                decryptMovementOrder();
                break;

            default:
                inputString += inChar;
                break;
        }
    }
}

void SerialReceiver::decryptMovementOrder() {
    int commaIndex = inputString.indexOf(',');
    if (commaIndex > 0) {
        angle = inputString.substring(0, commaIndex).toInt(); // before the ,
        if (angle < ANGLE_MIN || angle > ANGLE_MAX) {
            Serial.println("Angle must be between 48 and 138.");
            inputString = ""; // clear the string for the next command
            return;
        }
        speed = inputString.substring(commaIndex + 1).toInt();
        if (abs(speed) > SPEED_MAX) {
            Serial.println("Absolute speed must be between 300 and 6000.");
            inputString = ""; // clear the string for the next command
            return;
        }
        if (speed < 0) {
            stepper.setTargetPositionInSteps(-targetPosition);
            speed = abs(speed); // Reverse direction if speed is negative
        } else {
            stepper.setTargetPositionInSteps(targetPosition);
        }
        if (speed == 0) {
            stepper.setAccelerationInStepsPerSecondPerSecond(4000); // Stop the stepper if speed is 0
        } else {
            stepper.setAccelerationInStepsPerSecondPerSecond(2000); // Set acceleration for the stepper
        }

        servo.write(angle);
        stepper.setSpeedInStepsPerSecond(speed);
    } else {
        Serial.println("Invalid input format. Use 'angle,speed.'");
    }
    inputString = ""; // clear the string for the next command
}