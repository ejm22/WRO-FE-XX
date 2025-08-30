### Electrical Design Approach

#### 1\. Motorization

###### **1.1 Motor Option 1 : DC Motor**
DC motors are simple to control (on/off), useful for continuous forward movement, but require an encoder to determine position for precise tasks.
###### **1.2 Motor Option 2 : Stepper Motor**
Stepper motors move in discrete steps by activating electromagnets sequentially. They are ideal for short, precise movements and allow accurate position control without an encoder.
###### **1.3 Motor Choice**
We chose the stepper motor because it eliminates the need for an encoder, offers very precise position control (especially for parking), and is a new challenge to explore. The only complexity added is in task scheduling in software, which is manageable.
We also already had a NEMA 17 stepper motor, light and low consuming, which perfectly fitted on the base.
###### **1.4 Direction Control : Servo Motor**
A servo motor was selected for steering because it does not require a separate driver, has only three wires, and provides precise control.

---

#### 2\. Electric/Electronic Architecture

###### **2.1 Main Components Choice**
- **Processing:**  
  The robot uses a Raspberry Pi 5 as the master computer, handling camera input and all high-level decision logic. The Pi needs 5V at up to 3A.
- **Motor Control:**  
  An Arduino Uno R3 acts as the slave controller, receiving commands from the Pi and driving the motors. The Arduino requires 5V at 40mA (negligible).
- **Power:**  
  The stepper driver needs 12V. We use a 4s1p pack of 3.6V 18650 Li-Ion cells (14.4V, 2.85A). 14.4V is distributed via terminal blocks, then stepped down to 5V with a DC/DC converter for the Pi and Arduino.
- **Stepper Driver:**  
  The DRV8825 was chosen for its small size and micro-stepping ability (necessary for precise stepper control). Placed on a breadboard for easy connections.
- **Camera:**
  The Pi Camera 3 Wide module was chosen over the Pi Camera 3 module to have a wider field of view (FOV), necessary for more precision when parking, and helpful throughout the rest of the challenge as well.

---

#### 3. Wiring and Distribution
- **Terminal blocks** provide safe, compact power distribution for 14.4V and 5V rails.
- **Breadboard** is used for convenient connection of the stepper driver,  toggle switches, servo motor and other small electrical connections.
