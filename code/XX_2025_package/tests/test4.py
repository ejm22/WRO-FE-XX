import serial
import time
import math
import matplotlib.pyplot as plt

#time.sleep(2)

STEPPER_STEPS_PER_ROTATION =        200
WHEEL_DIAMETER_MM =                 55.6
WHEEL_PERIMETER_MM =                WHEEL_DIAMETER_MM*math.pi
DIFFERENTIAL_GEAR_RATIO =           20/28

MICROSTEP_ONE =                     1
MICROSTEP_ONE_HALF =                0.5
MICROSTEP_ONE_QUARTER =             0.25
MICROSTEP_ONE_HEIGHT =              0.125
MICROSTEP_OLNE_SIXTEEN =            0.0625

# Communication protocol with Arduino
# v : get the battery level in volts with 1 decimal
# m,value : set the microstepping on Arduino, value can be 1, 0.5, 0.25, 0.125, 0.625
# value1,value2. : set the direction (value1) and speed(value2), from 50 to 140 degrees and from xx to yy mm/second)
# t,value : set the target distance to reach

def control_led(arduino, state):
    if state == 'on':
        arduino.write(b'1')
        print("LED ON")
    elif state == 'off':
        arduino.write(b'0')
        print("LED OFF")

def get_battery_level(arduino):
    arduino.write(b'v')
    time.sleep(1)
    line=arduino.readline().decode().strip()
    if line:
        print(line)

def receive_data(arduino):
    data = ""
    while arduino.in_waiting > 0:
        data = arduino.read(arduino.in_waiting)
    number = int(data)
    print ("Data = ", number)
    return float(number)

def calculate_mm_per_step(microstepping):
    steps_per_rotation = STEPPER_STEPS_PER_ROTATION / microstepping
    mm_per_step = WHEEL_PERIMETER_MM / steps_per_rotation * DIFFERENTIAL_GEAR_RATIO
    return mm_per_step

def set_microstepping(arduino, value):
    message = f"m,{value}"
    message_bytes = message.encode('utf-8')
    arduino.write(message_bytes)

def set_direction_and_speed(direction, speed):
    message = f"{direction},{speed}."
    message_bytes = message.encode('utf-8')
    arduino.write(message_bytes)

def calculate_radius(angle):
    # Convert angle to radians
    angle_rad = math.radians(angle)
    if angle_rad != 0: # to avoid divison by zero
        radius = 165/math.cos(math.pi/2-angle_rad)
    else:
        radius = 100000.0
    #print("Radius = ", radius)
    return radius

def move_along_arc(x,y,alpha_deg, radius, arc_length):
    # Convert angle to radians
    alpha_rad = math.radians(alpha_deg)

    # Compute angle swept along the arc
    theta = arc_length / radius

    #Compute center of rotation
    center_x = x + radius*math.cos(alpha_rad + math.pi/2)
    center_y = y + radius*math.sin(alpha_rad + math.pi/2)

    #print("CenterX, CenterY ",center_x, center_y)

    # New angle from the center of rotation
    new_alpha_rad = alpha_rad + theta

    # Compute new position using the rotated offset
    new_x = center_x + radius*math.cos(new_alpha_rad - math.pi/2)
    new_y = center_y + radius*math.sin(new_alpha_rad - math.pi/2)

    #Convert back to degrees for orientation
    new_alpha_deg = math.degrees(new_alpha_rad) % 360

    return new_x, new_y, new_alpha_deg

def update_vehicle_position(arduino, x, y, alpha_deg, mm_per_step, old_direction_deg):
        
    # Receive the number of steps since last request
    arc_length = receive_data(arduino) * mm_per_step

    # Calculate the rotation radius based on the previous direction
    radius = calculate_radius(88-old_direction_deg)

    # Calculate the position and orientation
    x, y, alpha_deg = move_along_arc(x, y, alpha_deg, radius, arc_length)

    return x, y, alpha_deg


if __name__== '__main__':
    positions = []

    # Microstepping can be modified by software on Arduino
    microstepping =                     MICROSTEP_ONE_QUARTER # ***** still harcoded on Arduino

    # Set initial vehicle position and orientation
    x = y =                             0.0
    alpha_deg =                         0.0
    direction_deg =                     88  # Should be 0 degree instead for moving straight, to be converted by Arduino with offset

    # Connect to Arduino using USB
    arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    
    # Wait 2 seconds to let the communication link activate
    time.sleep(2)

    # Get the battery level and display the value
    get_battery_level(arduino)
    time.sleep(1)

    # Set the microstepping (NOT YET IMPLEMENTED ON ARDUINO, HARCODED)
    #set_microstepping(arduino, microstepping)

    # Calculate the mm_per_step
    mm_per_step = calculate_mm_per_step(microstepping)
    direction_speed_list = [[58, 3000],
                            [58, 3000],
                            [58, 3000],
                            [88, 3000],
                            [135, 3000],
                            [135, 3000],
                            [100, 3000],
                            [88, 3000],
                            [78, 3000],
                            [88, 3000]]
    # Instead of fixed value, direction would be computed by vision
    for i in range (0, 10):
        
        # Remember the previous direction to eventually compute the new vehicle position based on distance travelled
        old_direction_deg = direction_deg
        direction_deg = 58
        set_direction_and_speed(direction_deg, 2750)
        #direction_deg = direction_speed_list[i][0]
        #set_direction_and_speed (direction_deg, direction_speed_list[i][1])
        
        time.sleep (.05)
        x, y, alpha_deg = update_vehicle_position(arduino, x, y, alpha_deg, mm_per_step, old_direction_deg)
      
        print(f"x, y, angle = {x:.0f} {y:.0f} {alpha_deg:.0f}")
        positions.append((x,-y))

        time.sleep (.195)

    for i in range (0, 10):
        old_direction_deg = direction_deg
        direction_deg = 58

        set_direction_and_speed(direction_deg,0)
        time.sleep (.2)
        x, y, alpha_deg = update_vehicle_position(arduino, x, y, alpha_deg, mm_per_step, old_direction_deg)

        print(f"x, y, angle = {x:.0f} {y:.0f} {alpha_deg:.0f}")
        positions.append((x,-y))

    # Plot the path followed
    x_vals, y_vals = zip(*positions)
    plt.figure(figsize=(8,6))
    plt.plot(x_vals, y_vals, label="Path", linewidth=2)
    plt.scatter([x_vals[-1]], [y_vals[-1]], color='red', label = "end")
    plt.axis("equal")
    plt.show()
    while True:
        pass