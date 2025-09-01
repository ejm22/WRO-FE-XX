# WRO-FE-XX
Documentation for team Double-X's robot for WRO 2025 - Future Engineers.

---

## The Team
### Michael Bruneau

### Emile Jacques

---

## The Robot (Slef)
Have you ever had methods in your class needing the 'self' input to access the object ? If so, we are absolutely sure you've at least misstyped it once. Which is what we did throughout the entire project. With the amount of times Emile typed 'Slef', we had to give this name to our robot haha.

### Pictures

---

## Performance Videos
### Challenge 1

### Challenge 2

### Extra Informative Video

---

## Mechanical Overview

- **Wheels:** Spike Prime wheels (56mm diameter, 14mm thick) for compactness and grip.  
  [More details](mech/README_mech.md#11-wheel-choice)
- **Steering:** Ackermann geometry, 3D-printed after Lego prototyping.  
  [More details](mech/README_mech.md#12-steering-system)
- **Differential:** Compact Lego-built differential for rear wheels.  
  [More details](mech/README_mech.md#13-differential-rear-wheels)
- **Dimensions:** Max width ~150mm, length 285mm for tight turns and component fit.  
  [More details](mech/README_mech.md#14-dimensions-choice)
- **3D-Printed Structure:** Three-layer design (base, middle, top) for easy assembly and access.  
  [More details](mech/README_mech.md#3-final-3d-printed-structure)
- **Custom Mounts:** Holders for servo, stepper, switches, camera, and stepper coupler.  
  [More details](mech/README_mech.md#4-mounting-and-coupling)

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
