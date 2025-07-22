### Electrical Design Approach



#### 1\. Motorization

###### **1.1 Motor Option 1 : DC Motor**

A DC motor is either activated or deactivated. This feature is useful while move continuously forward since it only needs one signal to start. It requires an encoder to determine its position.



###### **1.2 Motor Option 2 : Stepper Motor**

A stepper motor moves when receiving pulses, which activate electromagnets, making the motor turn. It requires a constant feed of pulses being sent to move forward. The feature is useful while making short and precise movements, and it is easy to control its exact position, meaning it does not require an encoder to determine its position.



###### **1.3 Motor Choice**

We decided to choose the stepper motor, as we did not want to have to manage an encoder, being an extra component sending information we would need to manage. It is also more precise to know exactly how much the wheel turned, which is a useful feature for parking. The only difficulty it adds is to manage the program's tasks scheduling, which is manageable.



We also already had a NEMA 17 stepper motor, light and low consuming, which perfectly fitted on the base.



###### **1.4 Direction Control : Servo Motor**

A servo motor was the clear ideal choice. It doesn't require a driver, it only has three cables to manage, and it is precise.



#### 2\. Electric/Electronic Architecture

###### **2.1 Main Components Choice**

The challenge requires using a camera (for better results), to process the camera's data to then calculate how to control the motors, and to then send a signal to a micro controller, which will send power to the motors. 



We decided to use a **Raspberry Pi 5** (which we had) as the master, processing the camera's feed to then compute how the motors will move, and send the data to the micro controller. It requires 5V and uses 3A, which is the most consuming component on the robot.



We decided to use an **Arduino Uno R3** (which we also had) as the slave, controlling the motors via the orders received by the Pi. It requires 5V and uses itself only about 40mA, which is negligeable. 



The stepper motor driver needs 12V. We need a power source that can give minimum 12V. We chose to use **Li-Ion 3.6V 18650 batteries in 4s1p configuration**, giving up to 14.4V at 2.85A. We can power the driver directly with this voltage. Using terminal blocks, we can bring the 14.4V into a **DC/DC converter**, which will reduce the voltage to 5V, meaning the current will increase.



The stepper motor driver needed to be as small as possible to fit on the robot. We initially bought the DBH-12V driver, but quickly realized that it could not do micro-stepping, which is needed to precisely control the stepper motor. We then found the **DRV8825 driver**, a tiny driver able of doing micro-stepping, which we place on a breadboard to make the connections. 





