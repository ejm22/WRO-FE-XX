### Mechanical Design Approach
[All PNG, STP and STL files are in this directory](./CAD_3D_Printed_Pieces/)
#### 1\. Basic Mechanical Choices

###### **1.1 Wheel Choice**
We chose Spike Prime wheels (56mm diameter, 14mm thickness) for their compactness, grip on vinyl, and familiarity. Larger wheels would make the robot harder to control and take too much space; smaller wheels would complicate the design and lower ground clearance.
<img width="300" height="300" alt="image" src="https://github.com/user-attachments/assets/c5ac25da-1d0f-453b-8c17-f5e84693a9d4" />

###### **1.2 Steering System** 
- **Prototype:** Parallel beam Lego steering (two beams linked at ends) was tested. It suffered from drifting during turns due to both wheels turning at the same radius.
<img width="700" height="700" alt="image" src="https://github.com/user-attachments/assets/e486c290-8327-4dbd-909b-308bcbb0f6b9" />

- **Ackermann Steering:** Lego-based Ackermann system was built to solve drifting. Final version is 3D-printed to fit the custom base plate.
<img width="700" height="400" alt="image" src="https://github.com/user-attachments/assets/f464be3b-9783-44a1-b989-7284e19a2d47" />

<img width="700" height="400" alt="image" src="https://github.com/user-attachments/assets/e70a31a5-b710-4278-98e4-82efa7d4b4ed" />

###### **1.3 Differential (Rear Wheels)** 
A differential built out of Lego pieces individually bought on BrickLink allows the rear wheels to turn at different speeds for smooth cornering. Printing our own gears would have a low value/complexity ratio, so we built it with Lego pieces. It is very compact and works perfectly fine.
###### **1.4 Dimensions Choice**
We linked both the direction and differential wheel systems together. Considering all the components we would need to fit (Pi, Arduino, stepper motor, ...), we decided to keep a minimum approximate 50mm margin for the width, so max 150mm. A robot that has a big length/width ratio has a big turning radius (like a Formula 1 car). After testing different sizes, we decided to make the robot about 285mm long and 135mm wide. This makes the turning radius small enough to leave barely any room while turning around a pillar. 

---

#### 2\. Structural Prototypes

- **Lego Prototype:** Used 15-hole beams, L-beams, and frames to connect steering and differential systems.
- **Motor Positioning:** Stepper motor centrally located, axle connected to differential.
- **Wheel Space:** Front kept thin for steering range.
- **First Layer:** Held drive motor, DC/DC converter, and servo.
<img width="700" height="400" alt="image" src="https://github.com/user-attachments/assets/c30e563b-5177-4f33-b9d7-738bdfb9febb" />

---

#### 3\. Final 3D-Printed Structure

- **Base Plate:** Holds wheel systems, stepper, DC/DC, and servo.
<table>
  <tr>
    <td align="center">
      <strong>BasePlaqueV4 CAD</strong><br>
      <img src="https://github.com/user-attachments/assets/ed26cf6f-1e57-44ea-9111-e2258d0c9bfd" width="700" height="400">
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>BasePlaqueV4 Installation</strong><br>
      <img src="https://github.com/user-attachments/assets/85e35aba-d1d7-4a9b-9ccd-64304d10f4f9" width="700" height="400">
    </td>
  </tr>
</table>

___

- **Middle Plate:** Holds battery pack, Arduino, terminal blocks, stepper driver (on breadboard), and switches.
<table>
  <tr>
    <td align="center">
      <strong>MiddlePlaqueV4 CAD</strong><br>
      <img src="https://github.com/user-attachments/assets/753e8e88-8ea8-4e7f-975f-84e3ff07923b" width="700" height="400">
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>MiddlePlaqueV4 Installation</strong><br>
      <img src="https://github.com/user-attachments/assets/a77fad93-acb5-4cf7-8e73-98f99a5fe356" width="700" height="400">
    </td>
  </tr>
</table>

___

- **Top Plate:** Holds Raspberry Pi 5, Pi Camera, and driver terminal block.

<table>
  <tr>
    <td align="center">
      <strong>TopPlaqueV4 CAD</strong><br>
      <img src="https://github.com/user-attachments/assets/31292077-ac72-448d-aec0-7736a08eae95" width="700" height="400">
    </td>
  </tr>
</table>

___

- **3D Views of Complete Product**

<table>
  <tr>
    <td align="center">
      <strong>Left Side View</strong><br>
      <img src="https://github.com/user-attachments/assets/81fb3c33-7f9e-419c-99c4-76afcae5621d" width="700" height="400">
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Top View</strong><br>
      <img src="https://github.com/user-attachments/assets/0c307909-5943-4f71-b58f-66a1c21ec9f9" width="700" height="400">
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Bottom View</strong><br>
      <img src="https://github.com/user-attachments/assets/2bacd053-ec0a-4207-bb49-d4b5b8f2829f" width="700" height="400">
    </td>
  </tr>
</table>

- **Iterations:** As you can see in the following image, this was an iterative project with many versions of each part. 
<img width="1329" height="746" alt="image" src="https://github.com/user-attachments/assets/23bc6291-90cc-4661-bfed-2bcdd2166c82" />

---

#### 4\. Mounting and Coupling

- Custom holders for servo, stepper, switches, and camera.
<img width="700" height="400" alt="image" src="https://github.com/user-attachments/assets/835408aa-e0ad-429c-b7e4-860bc8e3e62b" />

___

- Stepper coupler connects motor to the differential.
<img width="700" height="400" alt="image" src="https://github.com/user-attachments/assets/3c08f9e3-0631-4f10-9adb-55721ab2cb71" />

