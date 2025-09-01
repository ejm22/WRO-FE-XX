### Mechanical Design Approach

#### 1\. Basic Mechanical Choices

###### **1.1 Wheel Choice**
We chose Spike Prime wheels (56mm diameter, 14mm thickness) for their compactness, grip on vinyl, and familiarity. Larger wheels would make the robot harder to control and take too much space; smaller wheels would complicate the design and lower ground clearance.
###### **1.2 Steering System** 
- **Prototype:** Parallel beam Lego steering (two beams linked at ends) was tested. It suffered from drifting during turns due to both wheels turning at the same radius.
- **Ackermann Steering:** Lego-based Ackermann system was built to solve drifting. Final version is 3D-printed to fit the custom base plate.

<img src="DirectionRods3.png" alt="Alt" width="100"/>

###### **1.3 Differential (Rear Wheels)** 
A Lego-built differential allows the rear wheels to turn at different speeds for smooth cornering. Printing our own gears would have a low value/complexity ratio, so we built it with Lego pieces. It is very compact and works perfectly fine.
###### **1.4 Dimensions Choice**
We linked both the direction and differential wheel systems together. Considering all the components we would need to fit (Pi, Arduino, stepper motor, ...), we decided to keep an approximate 50mm margin for the width, so max 150mm. A robot that has a big length/width ratio has a big turning radius (like a Formula 1 car). After testing different sizes, we decided to make the robot about 285mm long. This make the turning radius small enough to leave barely any room while turning around a pillar. 

---

#### 2\. Structural Prototypes

- **Lego Prototype:** Used 15-hole beams, L-beams, and frames to connect steering and differential systems.
- **Motor Positioning:** Stepper motor centrally located, axle connected to differential.
- **Wheel Space:** Front kept thin for steering range.
- **First Layer:** Held drive motor, DC/DC converter, and servo.

---

#### 3\. Final 3D-Printed Structure

- **Base Plate:** Holds wheel systems, stepper, DC/DC, and servo.
- **Middle Plate:** Holds battery pack, Arduino, terminal blocks, stepper driver (on breadboard), and switches.
- **Top Plate:** Holds Raspberry Pi 5, Pi Camera, and driver terminal block.

---

#### 4\. Mounting and Coupling

- Custom holders for servo, stepper, switches, and camera.
- Stepper coupler connects motor to the differential.
