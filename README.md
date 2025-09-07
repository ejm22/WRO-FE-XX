# WRO-FE-XX
Documentation for team Double-X's robot for WRO 2025 - Future Engineers.

---

## The Team
Team Double-X is made of 2 engineering students, Michael Bruneau and Emile Jacques, and we've been teammates since 2015 !  
[Our Facebook Page since 2015](https://www.facebook.com/1WROCanadaDoubleX)

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
  </tr>
</table>

---

<table>
  <tr>
    <td align="center"><strong>Top</strong><br><img src="https://github.com/user-attachments/assets/e5ef4c23-29e0-4840-b5ed-1ebd6015a973" width="300"></td>
    <td align="center"><strong>Front</strong><br><img src="https://github.com/user-attachments/assets/12b1a72a-31c1-4014-ae77-beca01701ed5" width="300"></td>
    <td align="center"><strong>Left</strong><br><img src="https://github.com/user-attachments/assets/01253a83-6a24-447f-accd-00e4e879fc58" width="300"></td>
  </tr>
  <tr>
    <td align="center"><strong>Bottom</strong><br><img src="https://github.com/user-attachments/assets/ef59c587-40d3-4308-bcb9-10ff51137080" width="300"></td>
    <td align="center"><strong>Back</strong><br><img src="https://github.com/user-attachments/assets/2b4324b6-ba22-49f1-9352-289231809b6f" width="300"></td>
    <td align="center"><strong>Right</strong><br><img src="https://github.com/user-attachments/assets/f753ad2e-17ea-4549-8277-479967388803" width="300"></td>
  </tr>
</table>

---

## Performance Videos
### Challenge 1
[Open Challenge Video on Youtube: ](https://youtu.be/OgR29EYXkdw)

### Challenge 2
[Obstacle Challenge Video on Youtube: ](https://youtu.be/s9inOFHvLYA)

---

## Mobility Management

- **Dimensions:** width 135mm, length 285mm for tight turns and component fit, height 248mm.  
  [Why we chose those dimensions](mech/README_mech.md#14-dimensions-choice)
- **Drive Motor:** NEMA 17 stepper (precise, no encoder needed).
We calculated the needed torque for our application, and considering a rolling resistance and an 85% gearbox efficiency, the NEMA-17's torque is greater than the needed torque. Here's how we calculated it : 
<img width="500" height="800" alt="image" src="https://github.com/user-attachments/assets/38c1d7ad-2134-4b28-865d-b25008afc42a" />

  [More Information on Drive Motor Choice](elec/README_elec.md#13-motor-choice)
- **Steering Motor:** Standard servo motor for simple, precise steering.  
  [More Information on Steering Motor Choice](elec/README_elec.md#14-direction-control--servo-motor)
- **3D-Printed Structure:** Three-layer design (base, middle, top) for easy assembly and access.  
<img src="https://github.com/user-attachments/assets/85e35aba-d1d7-4a9b-9ccd-64304d10f4f9" width="700" height="400">

<img src="https://github.com/user-attachments/assets/a77fad93-acb5-4cf7-8e73-98f99a5fe356" width="700" height="400">

<img src="https://github.com/user-attachments/assets/81fb3c33-7f9e-419c-99c4-76afcae5621d" width="700" height="400">

<img src="https://github.com/user-attachments/assets/0c307909-5943-4f71-b58f-66a1c21ec9f9" width="700" height="400">

<img src="https://github.com/user-attachments/assets/2bacd053-ec0a-4207-bb49-d4b5b8f2829f" width="700" height="400">

  [More Pictures & Info Here](mech/README_mech.md#3-final-3d-printed-structure)
- **Custom Mounts:** Holders for servo, stepper, switches, camera, and stepper coupler.  
  [Pictures Here](mech/README_mech.md#4-mounting-and-coupling)
- **Steering:** Initially parallel beams, now Ackermann geometry, 3D-printed after Lego prototyping. 
<img width="700" height="700" alt="image" src="https://github.com/user-attachments/assets/e486c290-8327-4dbd-909b-308bcbb0f6b9" />

<img width="700" height="400" alt="image" src="https://github.com/user-attachments/assets/e70a31a5-b710-4278-98e4-82efa7d4b4ed" />

  [Steering CADs](mech/README_mech.md#12-steering-system)
- **Wheels:** Spike Prime wheels (56mm diameter, 14mm thick) for compactness and grip.  
  [Why We Chose Spike Prime Wheels](mech/README_mech.md#11-wheel-choice)
- **Differential:** Compact differential for rear wheels, made of Lego pieces individually bought on BrickLink.  
  [Why We Chose This Differential](mech/README_mech.md#13-differential-rear-wheels)

- **Iterations:** As you can see in the following image, this was an iterative project with many versions of each part. 
<img width="1329" height="746" alt="image" src="https://github.com/user-attachments/assets/23bc6291-90cc-4661-bfed-2bcdd2166c82" />

#### Here's a general view of the robot in SolidWorks. The second picture is an exploded view of it, so you can see the detachable pieces.
<table>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/f869d26d-9c80-4198-b2c2-2d27d61f7edf" alt="Michael Bruneau" width="1000" height="1000" /></td>
    <td><img src="https://github.com/user-attachments/assets/625d4757-f4b7-4a0e-b886-05c6d8cfa581" alt="Emile Jacques" width="1000" height="1000" /></td>
  </tr>
</table>

### Controlling the Motors
This following document explains the C++ code used by the Arduino to control both the stepper and servo motors.  
[Motor Control](code/md/motor_control.md)

---

## Building Instructions
- **Parts list**\
Make sure you have all components ready before starting: 3D-printed parts, motors, drivers, electronics, screws, and connectors. A complete detailed table with quantities, sources, and usage is included below for reference.\
[Click here to open the parts list](XX_Parts_Lists.pdf)
- **3D Printing Parts**\
Using any 3D printer, start by 3D printing the necessary parts for the assembly. We used a Prusa Core 1. Every part needed has a STL file which you can use with any printer. If you're adventurous and want to modify a part, open the STEP file in your favorite CAD software. If you're unsure of what part you're printing, make sure to open the PNG file which contains a picture of the part.\
[Click here to open this folder](mech/CAD_3D_Printed_Pieces)
- **Adjust the Driver**\
The DRV8825 has a tiny screw to adjust the maximum current output. This isn't a big problem since the NEMA 17 stepper motor requires barely a few hundred mA, but it's good practice to set a limit. Use the DRV8825 Adjuster we custom-built to set this limit ! You can recreate this adjuster using the following drawing.\
[DRV8825 Adjuster Drawing](elec/Driver_Calibration_Circuit.pdf)
<table>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/516265fb-f433-4207-b433-87d9a1175ea5" alt="Michael Bruneau" width="300" height="400" /></td>
    <td><img src="https://github.com/user-attachments/assets/6ecc068c-e378-4e1c-9c0c-3960c86872ee" alt="Emile Jacques" width="300" height="400" /></td>
  </tr>
</table>

- **Assemble the Robot**\
Mechanically assembling the robot is quite straight-forward. The tricky part comes with the electrical connections. Make sure you follow correctly the following electrical drawings.\
*Take notes, the drawings are quite small ! Make sure to download the PDF files to be able to zoom.*\
[Electrical Drawings](elec/Electric_Planning.pdf)

---

## Power & Sense Management

- **Controller:** Raspberry Pi 5 (vision+logic, master) + Arduino Uno R3 (motor driver, slave).  
  [Why We Chose the Pi 5](elec/README_elec.md#21-main-components-choice)
- **Stepper Driver:** DRV8825 on breadboard (micro-stepping).  
  [Why We Chose the DRV8825](elec/README_elec.md#21-main-components-choice)
- **Camera:** Pi Camera 3 Wide for large FOV—helps with vision and parking.  
  [Why We Chose the Pi Camera 3 Wide](elec/README_elec.md#21-main-components-choice)
- **Wiring:** Terminal blocks and breadboard help organize and distribute power/signals.  
  [More details](elec/README_elec.md#3-wiring-and-distribution)
- **Power:** 4s1p 18650 Li-ion (14.4V) pack, DC/DC converter to 5V, terminal blocks for safe distribution.  

### Battery Runtime Calculation (1 hour at max load)
Here is the table of component power requirements : 

| Component                  | Voltage Requirement | Current Requirement |
|----------------------------|:------------------:|:------------------:|
| **Raspberry Pi 5**         | 5V                 | up to 3A           |
| **Arduino Uno R3**         | 5V                 | ~40mA              |
| **NEMA 17 Stepper Motor**  | 12V (via driver)   | Via Driver (so 0)  |
| **DRV8825 Stepper Driver** | 12V                | ~700mA             |
| **Servo Motor (steering)** | 5V                 | ~700mA             |
| **Pi Camera 3 Wide**       | 5V (via Pi)        | Via Pi (so 0)      |
| **DC/DC Converter**        | 14.4V in, 5V out   | 80% efficiency     |
| **4s1p 18650 Li-Ion Pack** | 14.4V              | up to 2.85A        |

Given the table, here's a quick calculation for **1 hour** of operation at maximum power:

#### Step 1: 5V Side Consumption
- Raspberry Pi 5: 3.00A  
- Arduino Uno R3: 0.04A  
- Servo Motor: 0.70A  
- **Total 5V current:** 3.74A  

**Power at 5V:**  
3.74A × 5V = **18.7W**

#### Step 2: Account for DC/DC Efficiency (80%)
**Battery power needed for 5V rail:**  
18.7W / 0.8 = **23.4W**

#### Step 3: Add Stepper Driver (12V side)
DRV8825: 0.70A × 12V = **8.4W**

#### Step 4: Total Battery Power & Current
**Total power from battery:**  
23.4W (5V rail) + 8.4W (stepper) = **31.8W**  
**Current from battery:**  
31.8W / 12V = **2.65A**

#### Step 5: Battery Capacity Needed (1 hour)
2.65A × 1h = **2.65Ah**

#### Conclusion
At full load, 1 hour of runtime requires **2.65Ah** at 12V.  
The 4s1p 18650 pack (2.85Ah) is just enough for 1 hour at max draw.

**In practice:** Most components use less than max (the Pi uses less than half), the robot is often idle, the DC/DC's efficiency is actually closer to 86%, and the stepper driver is disabled at 0 speed. In real use, the robot lasts 3–4 times longer, so the 4s1p pack is more than sufficient. We also have 8 cells in total so while 4 of them are used, the other 4 are charging, and it takes less time to charge batteries to full than to empty them.

### Security Measures
We added many security mesures on our robot to assure a safe robot and minimal reliability issues with parts.
- **Fuse:** We use a 3A fuse between the battery pack and the rest of the robot's electrical connexions to ensure the pack's safety.
- **Switches:** A Main Switch and a Driver Switch are installed. We are then able to shutdown the stepper motor in one click, or the entire robot in one different click.
- **Front Wing (Bumper):** A front wing was added to the front of the robot to make it crashproof. This keeps the important mechanical and electrical parts of the robot from absorbing the shock.
- **Terminal Blocks:** Terminal blocks were added for safer and easier electrical connexions. No short circuits in sight :)
- **Battery Pack Orientation:** Some of the cells would sometimes move too much from an impact between the robot and the wall, even with the bumper. By rotating the pack by 90 degrees, the cells won't be able to move.
- **Voltmeter:** A voltmeter was added on the side of the robot, connected right after the fuse, to show the battery pack's voltage. This is extremely useful since we preferably never want our voltage to go below 10.8V (for cell preservation). 

---

## Obstacle Management

### Vision Methods and Decision Making

This part of the readme explains how the computer vision pipeline drives steering decisions for the robot. It explains the following:
- Wall following (how far up the image it sees black on both sides)
- Obstacle handling
- Inner/outer crash detection
- Arbitration (how actions are chosen)

### 1) Image pipeline (inputs used by algorithms)

The camera pipeline produces these images used by the algorithms:
- polygon_image: binary map of the drivable corridor (walls are black=0, free space is white=255)
- display_image: BGR frame used for debug overlays (text, lines, circles)
- obstacle_image / pink_obstacle_image: binary masks for color obstacles
- blueline_image & orangeline_image: per-color masks for lap tracking

<table>
  <tr>
    <td align="center">
      <strong>Display Image Open Challenge</strong><br>
      <img src="https://github.com/user-attachments/assets/924e428f-c0ea-4ef4-959d-12420b2773ab" width="700">
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Display Image Obstacle Challenge</strong><br>
      <img src="https://github.com/user-attachments/assets/f61b0e58-9b93-4888-8548-6ec4ca5e9cb8" width="700">
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Polygon Image</strong><br>
      <img src="https://github.com/user-attachments/assets/c8e8c91d-449f-45dc-88c7-7d1e1df058a3" width="700">
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Obstacle Image</strong><br>
      <img src="https://github.com/user-attachments/assets/35c2a820-98f5-4030-97ef-c1d3fdaa19da" width="700">
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Lines Image</strong><br>
      <img src="https://github.com/user-attachments/assets/186cd617-33ae-475b-ba15-ccbb2e6fb1e4" width="700">
    </td>
  </tr>
</table>

See [`CameraManager`](code/XX_2025_package/classes/camera_manager.py) and [`ImageTransformUtils`](code/XX_2025_package/utils/image_transform_utils.py).

### 2) Wall following calculations

Goal: steer so that the nearest wall is observed at a desired “depth” (how far up the image) and “lateral” position (how far from the side).

How it works:
- The robot scans for black (wall) pixels:
  - Bottom-up along a small band of columns near the followed side (“how far up” the wall appears).
  - Side-in from the image center toward the followed side along a small band of rows (“how far inward” the wall appears).
- These samples are averaged into (avg_x, avg_y) by [`ImageAlgorithms.find_wall_to_follow`](code/XX_2025_package/classes/image_algoriths.py).
- [`ImageAlgorithms.calculate_servo_angle_from_walls`](code/XX_2025_package/classes/image_algoriths.py) builds a PD-like controller:
  - Proportional term: error = (avg_x + avg_y) − threshold.
  - Derivative term: change of that error across frames.
  - Direction sign (LEFT/RIGHT) is taken from context to steer the correct side.
- Gains and the target threshold come from [`CHALLENGE_CONFIG`](code/XX_2025_package/classes/image_algoriths.py) via [`ImageAlgorithms.calculate_wall_threshold_kp_kd`](code/XX_2025_package/classes/image_algoriths.py), adapting behavior per challenge/lap.
- Corner detection: a large negative jump in the wall error derivative marks a “corner,” returned via the is_corner flag for higher-level logic.

Notes:
- “How far up it sees black on both sides” is embodied in the dual scans (bottom-up and side-in) that together capture corridor geometry.

### 3) Obstacle handling calculations

When an obstacle is present (green/red/pink block), the robot computes an avoidance “object line,” converts it to an angle, and arbitrates with wall following.

Process in [`ImageAlgorithms.find_obstacle_angle_and_draw_lines`](code/XX_2025_package/classes/image_algoriths.py):
- Safety first: [`ImageAlgorithms.check_outer_wall_crash`](code/XX_2025_package/classes/image_algoriths.py). If a frontal collision risk is detected, immediately force a sharp evasive turn.
- Find the largest obstacle rectangle on the color mask and classify its color using HSV.
- Draw a guidance line from the obstacle center to a safe floor target x:
  - Green → pass on the right; Red → pass on the left (policy).
- Convert that line’s geometry into an object angle, then map it to a servo angle with a color-specific offset in [`ImageAlgorithms.calculate_servo_angle_from_obstacle`](code/XX_2025_package/classes/image_algoriths.py).
- Inner safety: [`ImageAlgorithms.check_inner_wall_crash`](code/XX_2025_package/classes/image_algoriths.py) disables obstacle passing if the inner wall is too close (falls back to wall following).

What the “mapping” does:
- It shifts and scales the object angle around straight-ahead so the servo turns just enough to skirt the obstacle, clamped to safe servo limits.

### 4) Crash detection

Two safety checks override normal behavior:
- Outer wall crash: [`ImageAlgorithms.check_outer_wall_crash`](code/XX_2025_package/classes/image_algoriths.py) probes a fixed point ahead, and if it’s black in the polygon image, commands an emergency turn away from the outer wall.
- Inner wall crash: [`ImageAlgorithms.check_inner_wall_crash`](code/XX_2025_package/classes/image_algoriths.py) probes several points near the inner side; if too close (especially with a short obstacle), obstacle passing is suppressed.

### 5) Arbitration: choosing the action

Both proposals are produced:
- Wall-following angle from [`ImageAlgorithms.calculate_servo_angle_from_walls`](code/XX_2025_package/classes/image_algoriths.py)
- Obstacle angle from [`ImageAlgorithms.calculate_servo_angle_from_obstacle`](code/XX_2025_package/classes/image_algoriths.py) (or None if no obstacle)

Selection rule in [`ImageAlgorithms.choose_output_angle`](code/XX_2025_package/classes/image_algoriths.py):
- If there is a valid obstacle-avoidance angle, prefer it; otherwise, follow the wall.

Priority in practice:
1) Outer wall crash → emergency avoidance
2) Valid obstacle avoidance → use it
3) Inner wall too close while avoiding → fall back to wall following
4) Otherwise → wall following

### 6) Tuning notes

- Controller gains/thresholds are challenge-aware via [`CHALLENGE_CONFIG`](code/XX_2025_package/classes/image_algoriths.py) and refined per lap in [`ImageAlgorithms.calculate_wall_threshold_kp_kd`](code/XX_2025_package/classes/image_algoriths.py).
- The direction (LEFT/RIGHT) simply flips the sign of the control so one algorithm works for both sides.
- Corner detection from the wall controller’s derivative is used elsewhere (for example during parking) to trigger special maneuvers.

───────────────

### Block diagrams:
<table>
  <tr>
    <td align="center">
      <strong>Open Challenge Block Diagram</strong><br>
      <img src="https://github.com/user-attachments/assets/e95b79d5-b4a5-4368-99a4-92471d40a730" width="727" height="856">
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Obstacle Challenge Block Diagram</strong><br>
      <img src="https://github.com/user-attachments/assets/ed6850e3-6d91-4450-8487-a04476d74ad9" width="796" height="1002">
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Obstacle Challenge Action Decisions</strong><br>
      <img src="https://github.com/user-attachments/assets/d5e8e839-0882-47c3-935e-1129bcbaee61" width="598" height="601">
    </td>
  </tr>
</table>

### Extras
- Lap tracking and direction detection [details here.](code/md/laps_and_direction.md)
- Parking [details here.](code/md/parking.md)

---

## Software Key Components

- **Communication:** Serial communication via USB cable between Arduino and Pi (using custom protocol).\
  [Communications Protocol Details](code/md/communication.md)
- **Raspberry Pi Environment Setup:** Downloading utilities on your Pi, creating a virtual environment (venv), and installing dependencies.\
  [How to Setup your Raspberry Pi](code/md/raspberry_pi_setup.md)

---
