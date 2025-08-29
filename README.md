# WRO-FE-XX

This GitHub contains the documentation and every detail of team Double-X's robot for WRO 2025, from the CAD files of the chassis to Raspberry Pi's decision making. 

## The Team
### Michael Bruneau

### Emile Jacques

## The Robot (Slef)
### Pictures

## Performance Videos
### Challenge 1

### Challenge 2

### Extra Informative Video

## How It Works : Mechanical Basics
### Mechanical Design
#### Choice of Form Factor

#### Choice of Wheels
We decided to use Spike Prime wheels. They have a 56mm outer diameter and 14mm thickness, which is ideal since they don't use much space. Big wheels would make the robot faster and difficult to control, and would take too much space when turning. Smaller wheels would make the base design very complex and would limit the components we could use since everything would be barely above the ground. The Spike Prime wheels also have lots of grip on vinyl surfaces. Lastly, we've used Spike Prime wheels in past projects and we were very satisfied.

#### Choice of Steering System
##### Version 1 : Parallel Beams (Lego-based)
We decided to build a Lego prototype of a parallel direction. It used two 13 hole beams linked at both ends by H-pieces which had axles leading to the wheels. One of the beams would be fully connected to the base, the other would be moved by the moving piece connected both beams.
The main problem with this type of direction is the drifting caused by the wheels. When turning, the inside wheel (wheel on the side the robot is turning) will have a smaller turning radius, which will cause it to drift since the outside wheel tries to turn with the same radius.
(See image below)

##### Version 2 : Ackermann Steering (Lego-based)
To solve the drifting issue, we built an Ackermann steering system. When turning, the inside wheel will have a greater angle than the outside wheel, leading to a smooth turn. 
(See image below)

##### Version 3 : Ackermann Steering (3D-Printed)
For the final version of the robot, we designed the Ackermann steering in SolidWorks. The steering CAD was conceived in accordance with the base plate CAD, perfectly fitting M5 screws. This step removed Lego pieces. 
(See image below)

#### Minimization of Turning Radius
Talk about the steering range with current distance between beams, ...

### Drive System Components
#### Drive Motor Selection
##### Option 1 : DC Brush / Brushless Motor
Option 1 was to take a normal DC motor. We could use a motor with brushes, which is cheaper and does not require a driver, or use a brushless motor, which requires a driver, but has less internal friction and is overall better for long activations. Regardless, an encoder is required to know the motor's current position, which is essential for the parallel parking. The robot needs to be extremely precise, and without an encoder, it would need to be activated for an amount of seconds. As we learned with EV3 Mindstorms in previous years, moving according to time isn't reliable, since the battery level might influence the motor's speed. 

##### Option 2 : Stepper Motor
Option 2 was to take a stepper motor. This kind of motor uses a set number of magnets, which active or deactivate, to turn the motor by 'x' steps. It requires a driver which receives the pulses (steps) and a direction. The motor can't turn freely if the driver is activated, since the magnets will activate and lock the motor.

##### Final Choice : Stepper Motor
Talk about : we had a stepper, we didn't want to use an encoder, it's a new challenge & option we wanted to explore, very precise

##### Driver Choice for Stepper Motor
Talk about the DRV8825

#### Steering Motor Selection

#### Rear Wheels Gearbox (Differential)

### Robot Structure
#### Version 1 : First Layer Structure (Lego-based)
Talk about having a very basic layout of the robot, space for front wheels, space for stepper motor

#### Version 2 : Base Plate Structure (3D-printed)
Talk about printing the base plate, iterations of it, placing stepper, DC/DC, gearbox, servo, ...
Talk about having cardboard boxes stacked to imagine where Pi and Arduino are placed, ...

#### Version 3 : Final Main Structure (3D-printed)
Talk about mounting each layer (screw, threads, ...), and iterations
##### Base Plate

##### Middle Plate

##### Top Plate

### Mounting and Coupling Components
#### Holders
Servo holder, stepper holder, switch holder, camera holder
#### Front Wing

#### Stepper Coupler

## How It Works : Electrical Architecture
