### Mechanical Design Approach



1. #### Basic Mechanical Choices

###### **1.1 Wheel Choice**

We decided to use Spike Prime wheels. They have a 56mm outer diameter and 14mm thickness, which is ideal since they don't use much space. Big wheels would make the robot faster and difficult to control, and would take too much space when turning. Smaller wheels would make the base design very complex and would limit the components we could use since everything would be barely above the ground. The Spike Prime wheels also have lots of grip on vinyl surfaces. 



###### **1.2 Wheel System 1 : Direction** 

We decided to build a Lego prototype of a parallel direction. It uses two 13 hole beams linked at both ends by H-pieces which have axles leading to the wheels. One of the beams would be fully connected to the base, the other would be moved by the moving piece connected both beams *(See image below)*. The Ackermann direction is usually better, but in this case, the value/complexity ratio isn't high enough.



###### **1.3 Wheel System 2 : Differential** 

The differential is useful to have the rear wheels going at different speeds while turning. Printing our own gears would have a low value/complexity ratio, so we built it with Lego pieces. It is very compact and works perfectly fine.



###### **1.4 Dimensions Choice**

We linked both the direction and differential wheel system together to decide the best length and width. We had to consider all the components we would need to fit (Pi, Arduino, stepper motor, ...). We decided to keep an approximate 50mm margin for the width, so max 150mm. A robot that has a big length/width ratio has a big turning radius (like a Formula 1 car) so we decided to make the robot about 220mm long. This make the turning radius small enough to leave barely any room while turning around a pillar. 



#### 2\. Structure Prototype

###### **2.1 Pieces for Prototype**

The prototype for the structure was made out of Lego pieces. We connected the direction and differential wheel systems with 15-hole beams, L beams and frames. 



###### **2.2 Motor Positioning** 

A space in the middle would fit a motor, with its axle connecting with the differential entry. 



###### **2.3 Wheel Space**

The front of the base had to be thin, so the wheels can turn freely.



###### **2.4 Electronic Components' Layout**

The Lego-built base represented the first layer of components. This layer would fit the rear-drive motor, the DC/DC converter and the servo motor (direction). 



#### 3\. Structure

Each following piece is 3D printed in the Prusa Core One in PLA.

###### **3.1 Base Plate**

The base plate holds both wheel systems, the stepper motor, the DC/DC converter and the servo motor. 



###### **3.2 Middle Plate** 

The middle plate holds the battery pack, the Arduino Uno, the 5V and 12V terminal blocks, the stepper motor driver, its breadboard, and the two power switches. 



###### **3.3 Top Plate**

The top plate hold the Raspberry Pi 5, the Pi Camera 3, and the driver's terminal block. 





