import serial
import time
import math

#time.sleep(2)

def control_led(arduino, state):
    if state == 'on':
        arduino.write(b'1')
        print("LED ON")
    elif state == 'off':
        arduino.write(b'0')
        print("LED OFF")

def setup_arduino(arduino):
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

def calculate_radius(angle):
    if angle != 0:
        radius = 165/math.cos(angle)
    else:
        radius = 10000.0
    #print("Radius = ", radius)
    return radius

def move_along_arc(x,y,alpha_deg, radius, arc_length):
    # Convert angle to radians
    alpha_rad = math.radians(alpha_deg)
    #print("Alpha_rad = ", alpha_rad)

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

if __name__== '__main__':
    x=y=0.0
    alpha_deg = 0.0
    steps_per_rotation = 800
    wheel_diameter = 55.6
    wheel_perimeter = wheel_diameter*math.pi
    mm_per_step = wheel_perimeter / steps_per_rotation



    arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    time.sleep(2)

    setup_arduino(arduino)
    time.sleep(1)

    for i in range (0, 10):
        
        arduino.write(b'58,2350.')
        time.sleep (.05)
        
        arc_length = receive_data(arduino) * mm_per_step
        radius = calculate_radius(90-58)
        x, y, alpha_deg = move_along_arc(x, y, alpha_deg, radius, arc_length)
        print("x, y, alpha_deg = ", x, y, alpha_deg)

        time.sleep (.195)
        #arduino.write(b'88,4000.')
        #time.sleep(1.5)    
        #arduino.write(b'88,-4000.')
        #time.sleep(1.5)    
        #arduino.write(b'110,1000.')
        #time.sleep(1)    
        #arduino.write(b'100,2000.')
        #time.sleep(1)    
        #arduino.write(b'80,-1000.')
        #time.sleep(1)    
        #arduino.write(b'88,0.')
        #time.sleep(1)
    for i in range (0, 10):
        arduino.write(b'88,0.')
        time.sleep (.2)
        arc_length = receive_data(arduino) * mm_per_step
        radius = calculate_radius(90-58)
        x, y, alpha_deg = move_along_arc(x, y, alpha_deg, radius, arc_length)
        print("x, y, alpha_deg = ", x, y, alpha_deg)
