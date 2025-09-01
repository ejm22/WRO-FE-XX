# WRO-FE-XX
Documentation for team Double-X's robot for WRO 2025 - Future Engineers.

---

## The Team
Team Double-X is made of 2 engineering students, Michael Bruneau and Emile Jacques, and we've been teammates since 2015 !

<table>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/ea431a0c-9627-4ab4-8209-1c5feedf7716" alt="Michael Bruneau" width="400" height="300" /></td>
    <td><img src="https://github.com/user-attachments/assets/7559d462-5953-40f4-a1f0-3e67d9a98dc4" alt="Emile Jacques" width="400" height="300" /></td>
  </tr>
</table>

---

## The Robot (Slef)
Have you ever had methods in your class needing the 'self' input to access the object ? If so, we are absolutely sure you've at least misstyped it once. Which is what we did throughout the entire project. With the amount of times Emile typed 'Slef', we had to give this name to our robot haha.

### Pictures
<table>
  <tr>
    <td align="center"><strong>GIF</strong><br><img src="https://github.com/user-attachments/assets/337494ee-50da-42a9-8c70-eba4d5f09ea6" width="300"></td>
    <td align="center"><strong>Front</strong><br><img src="https://github.com/user-attachments/assets/12b1a72a-31c1-4014-ae77-beca01701ed5" width="300"></td>
    <td align="center"><strong>Back</strong><br><img src="https://github.com/user-attachments/assets/2b4324b6-ba22-49f1-9352-289231809b6f" width="300"></td>
  </tr>
  <tr>
    <td align="center"><strong>Left</strong><br><img src="https://github.com/user-attachments/assets/01253a83-6a24-447f-accd-00e4e879fc58" width="300"></td>
    <td align="center"><strong>Right</strong><br><img src="https://github.com/user-attachments/assets/f753ad2e-17ea-4549-8277-479967388803" width="300"></td>
    <td align="center"><strong>Top</strong><br><img src="https://github.com/user-attachments/assets/e5ef4c23-29e0-4840-b5ed-1ebd6015a973" width="300"></td>
  </tr>
</table>

---

## Performance Videos
### Challenge 1

### Challenge 2

### Extra Informative Video

---

## Mechanical Overview

- **Dimensions:** Max width ~150mm, length 285mm for tight turns and component fit.  
  [More details](mech/README_mech.md#14-dimensions-choice)
- **3D-Printed Structure:** Three-layer design (base, middle, top) for easy assembly and access.  
  [More details](mech/README_mech.md#3-final-3d-printed-structure)
- **Custom Mounts:** Holders for servo, stepper, switches, camera, and stepper coupler.  
  [More details](mech/README_mech.md#4-mounting-and-coupling)
- **Steering:** Ackermann geometry, 3D-printed after Lego prototyping.  
  [More details](mech/README_mech.md#12-steering-system)
- **Wheels:** Spike Prime wheels (56mm diameter, 14mm thick) for compactness and grip.  
  [More details](mech/README_mech.md#11-wheel-choice)
- **Differential:** Compact Lego-built differential for rear wheels.  
  [More details](mech/README_mech.md#13-differential-rear-wheels)

#### Here's a general view of the robot in SolidWorks. The second picture is an exploded view of it, so you can see the detachable pieces.
<table>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/f869d26d-9c80-4198-b2c2-2d27d61f7edf" alt="Michael Bruneau" width="1000" height="1000" /></td>
    <td><img src="https://github.com/user-attachments/assets/625d4757-f4b7-4a0e-b886-05c6d8cfa581" alt="Emile Jacques" width="1000" height="1000" /></td>
  </tr>
</table>

---

## Electrical & Electronic Overview

- **Drive Motor:** NEMA 17 stepper (precise, no encoder needed).  
  [More details](elec/README_elec.md#13-motor-choice)
- **Steering:** Standard servo motor for simple, precise steering.  
  [More details](elec/README_elec.md#14-direction-control--servo-motor)
- **Controller:** Raspberry Pi 5 (vision+logic, master) + Arduino Uno R3 (motor driver, slave).  
  [More details](elec/README_elec.md#21-main-components-choice)
- **Power:** 4s1p 18650 Li-ion (14.4V) pack, DC/DC converter to 5V, terminal blocks for safe distribution.  
  [More details](elec/README_elec.md#21-main-components-choice)
- **Stepper Driver:** DRV8825 on breadboard (micro-stepping).  
  [More details](elec/README_elec.md#21-main-components-choice)
- **Camera:** Pi Camera 3 Wide for large FOV—helps with vision and parking.  
  [More details](elec/README_elec.md#21-main-components-choice)
- **Wiring:** Terminal blocks and breadboard help organize and distribute power/signals.  
  [More details](elec/README_elec.md#3-wiring-and-distribution)

---

## Software & Logic Overview

- **Communication:** Serial communication via USB cable between Arduino and Pi (using custom protocol).\
  [More details](code/communication_draft.md)
- **Raspberry Pi Environment Setup:** Downloading utilities on your Pi, creating a virtual environment (venv), and installing dependencies.\
  [More details](code/raspberry_pi_setup.md)

## Building Instructions
- **3D Printing Parts**
Using any 3D printer, start by 3D printing the necessary parts for the assembly. Every part needed has a STL file which you can use with any printer. If you're adventurous and want to modify a part, open the STEP file in your favorite CAD software. If you're unsure of what part you're printing, make sure to open the PNG file which contains a picture of the part.
[Click here to open this folder](mech/CAD_3D_Printed_Pieces)
- **Assemble the Robot**
Mechanically assembling the robot is quite straight-forward. The tricky part comes with the electrical connections. Make sure you follow correctly the following electrical drawings.
[Electrical Drawings](elec/Electric_Planning.pdf)
