# How We Control the Motors

This document explains how the drive and steering motors of Team Double-X's robot are controlled using Arduino, focusing on our actual implementation and challenges.

---

## 1. Overview

Our robot uses:
- **NEMA 17 Stepper Motor** for driving the rear wheels (precise position & speed control).
- **Servo Motor** for steering the front wheels (Ackermann geometry).

The motors are controlled by an **Arduino Uno R3** that receives high-level commands from a Raspberry Pi 5 and drives the motors using dedicated libraries and electronic drivers.

---

## 2. Hardware Architecture

- **Stepper Motor Driver:** DRV8825, chosen for its microstepping ability and compact design.
- **Connections:**  
  - Stepper motor uses STEP, DIR, and ENABLE pins.
  - Servo motor uses a single PWM pin (ANGLE_PIN).
- **Power:**  
  - Stepper driver powered by 12V from a Li-Ion pack.
  - Arduino and Pi powered via a DC/DC converter.

---

## 3. Arduino Software Implementation

Our code for motor control is written in C++ and runs on the Arduino. The logic is split between stepper (drive) and servo (steering) control.

### Stepper Motor Control (Drive)

A stepper motor functions by receiving pulses which activate and deactivate magnets, turning the motor. When decelerating, a stepper can't keep its precision if it stops receiving steps, hence why we need to gradually lower the speed. We use the FlexyStepper library, because it can manage those decelerations. The command logic is our own. The driver is **enabled** only when movement is required; otherwise, it is disabled to prevent overheating.

```cpp
#include <FlexyStepper.h>

const int DIR_PIN = 10;
const int STEP_PIN = 9;
const int ENABLE_PIN = 2;

FlexyStepper stepper;

void setup() {
    stepper.connectToPins(STEP_PIN, DIR_PIN);
    pinMode(ENABLE_PIN, OUTPUT);
    digitalWrite(ENABLE_PIN, LOW); // Enable driver by default
}

void loop() {
    // Example: Move the robot if a command is received
    if (shouldMove()) {
        digitalWrite(ENABLE_PIN, LOW); // Enable driver
        stepper.setSpeedInStepsPerSecond(commandedSpeed);
        stepper.setAccelerationInStepsPerSecondPerSecond(2000);
        stepper.moveRelativeInSteps(commandedSteps);
    } else if (currentSpeedIsLowEnough()) {
        digitalWrite(ENABLE_PIN, HIGH); // Disable driver to avoid overheating
    }
}
```

### Servo Motor Control (Steering)

Steering is achieved with a standard Servo library. The servo receives new angles as commands are processed.

```cpp
#include <Servo.h>
const int ANGLE_PIN = 11;

Servo steeringServo;

void setup() {
    steeringServo.attach(ANGLE_PIN);
}

void loop() {
    int steeringAngle = getSteeringAngle();
    steeringServo.write(steeringAngle); // Angle: 36-136
}
```
*Note: The angle at which the servo is straight is 86 degrees. The maximum angles for our Ackermann steering are 36 and 136 degrees.*

---

## 4. Control Flow

1. **Command Reception:**  
   The Pi sends commands to the Arduino (distance, speed, steering angle).
2. **Motion Execution:**  
   - Arduino sets the stepper speed, servo angle, and target position.
   - Driver ENABLE is managed based on demand and speed.
3. **Safety & Scheduling:**  
   - The driver is disabled when no motion is needed, or the speed is near zero, to prevent overheating.
   - Motion complete functions ensure safe synchronization.

---

## 5. Temperature Analysis

A major issue we encountered is **driver overheating**. The DRV8825 gets extremely hot even with moderate use, especially if it's left enabled while idle. To address this, our code disables the driver whenever:
- The demanded speed is zero and the actual speed is low enough.
- No commands are received for a while.

Below are thermal images showing the results of our code:

<table>
  <tr>
    <td><img src="DRIVER_TEMP_IMAGE_1_URL" alt="Driver Temp 1" width="350"></td>
    <td><img src="DRIVER_TEMP_IMAGE_2_URL" alt="Driver Temp 2" width="350"></td>
  </tr>
  <tr>
    <td><img src="DRIVER_TEMP_IMAGE_3_URL" alt="Driver Temp 3" width="350"></td>
    <td><img src="DRIVER_TEMP_IMAGE_4_URL" alt="Driver Temp 4" width="350"></td>
  </tr>
</table>

*Images show that the driver temperature is around 40 degrees Celsius, which is very normal. We do not have pictures, but it would previously be so hot that touching the driver could cause serious burns*

---

## 6. References

- [FlexyStepper Library Documentation](https://github.com/Stan-Reifel/FlexyStepper)
- [DRV8825 Datasheet](https://www.ti.com/lit/ds/symlink/drv8825.pdf?HQS=dis-dk-null-digikeymode-dsf-pf-null-wwe&ts=1752710261679)
- [Driver Circuit Used on our Robot: How to Adjust Current Limit](https://www.makerguides.com/drv8825-stepper-motor-driver-arduino-tutorial/)
- *Main Arduino code: [`code/arduino/src/main.cpp`](../code/arduino/src/main.cpp)*

---
