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

            case 'm':
            case 'M':
                decryptMovementOrder('m');
                break;
            
            case 't':
            case 'T':
                decryptMovementOrder('t');
                break;
                
            default:
                break;
        }
    }
}

void SerialReceiver::decryptMovementOrder(char action) {
    inputString = ""; // Clear the letter out of the input string
    char inChar;
    while (inChar != '.') {
        if (Serial.available()){
            inChar = (char)Serial.read();
            inputString += inChar;
        }
    }
    int firstComma = inputString.indexOf(',');
    int secondComma = -1; // Initialize second comma index
    long int newTarget = targetPosition; // Initialize new target position
    if (firstComma > 0) {
        // Read angle
        angle = inputString.substring(0, firstComma).toInt(); // before the ,
        // Read speed
        if (action == 't') {    // Check if there's a second comma for target position
            secondComma = inputString.indexOf(',', firstComma + 1);
            speed = inputString.substring(firstComma + 1, secondComma).toInt();
            newTarget = long(-inputString.substring(secondComma + 1).toInt()); // after the second ,
            if (speed < 0) {
                stepper.setTargetPositionRelativeInSteps(-newTarget);
                speed = abs(speed); // Reverse direction if speed is negative
            } else {
                stepper.setTargetPositionRelativeInSteps(newTarget);
            }
        }
        else {
            speed = inputString.substring(firstComma + 1).toInt(); // after the ,
            if (speed < 0) {
                stepper.setTargetPositionInSteps(-newTarget);
                speed = abs(speed); // Reverse direction if speed is negative
            } else {
                stepper.setTargetPositionInSteps(newTarget);
            }
        }
        //Validate angle
        if (angle < ANGLE_MIN || angle > ANGLE_MAX) {
            Serial.println("Angle must be between 48 and 138.");
            inputString = ""; // clear the string for the next command
            return;
        }
        // Validate speed
        if (abs(speed) > SPEED_MAX) {
            Serial.println("Absolute speed must be between 300 and 6000.");
            inputString = ""; // clear the string for the next command
            return;
        }
        // No need to validate target position as it can be any long integer
        // Invert target position if speed is negative
        
        // Set the acceleration based on speed : fast acceleration for stops, slow for normal movement
        if (speed == 0) {
            stepper.setAccelerationInStepsPerSecondPerSecond(4000); // Stop the stepper if speed is 0
        } else {
            stepper.setAccelerationInStepsPerSecondPerSecond(2000); // Set acceleration for the stepper
        }
        // Update angle and speed
        servo.write(angle);
        stepper.setSpeedInStepsPerSecond(speed);
    }
    else {
        Serial.println("Invalid input format. Use 'angle,speed.'");
    }
    inputString = ""; // clear the string for the next command
}