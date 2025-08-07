import serial
import time
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading

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

class MapPlotter:
    def __init__(self):
        self.old_direction_deg = 88
        self.old_speed = 0
        self.x = 0.0
        self.y = 0.0
        self.alpha_deg = 0
        self.direction_deg = 88 # should also be zero if 88 normalized to zero
        self.mm_per_step = 0
        self.time_stamp = time.time()
        self.x_data = []
        self.y_data = []
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], 'b-')
        self.ax.set_xlim (-2000, 2000)
        self.ax.set_ylim (-2000, 2000)
        self.direction_speed_list = [[88, 1000],
                            [88, 1000],
                            [88, 1000],
                            [88, 1000],
                            [88, 1000],
                            [88, 1000],
                            [88, 1000],
                            [88, 1000],
                            [88, 1000],
                            [88, 1000]]



    def calculate_mm_per_step(self,microstepping):
        steps_per_rotation = STEPPER_STEPS_PER_ROTATION / microstepping
        self.mm_per_step = WHEEL_PERIMETER_MM / steps_per_rotation * DIFFERENTIAL_GEAR_RATIO

    def set_direction_and_speed(self,direction, speed):
        message = f"{direction},{speed}."
        message_bytes = message.encode('utf-8')
        arduino.write(message_bytes)

    def calculate_radius(self, angle):
        # Convert angle to radians
        angle_rad = math.radians(angle)
        if angle_rad != 0: # to avoid divison by zero
            radius = 165/math.cos(math.pi/2-angle_rad)
        else:
            radius = 100000.0
        #print("Radius = ", radius)
        return radius

    def move_along_arc(self, radius, arc_length):
        # Convert angle to radians
        alpha_rad = math.radians(self.alpha_deg)

        # Compute angle swept along the arc
        theta = arc_length / radius

        #Compute center of rotation
        center_x = self.x + radius*math.cos(alpha_rad + math.pi/2)
        center_y = self.y + radius*math.sin(alpha_rad + math.pi/2)


        # New angle from the center of rotation
        new_alpha_rad = alpha_rad + theta

        # Compute new position using the rotated offset
        self.x = center_x + radius*math.cos(new_alpha_rad - math.pi/2)
        self.y = center_y + radius*math.sin(new_alpha_rad - math.pi/2)

        #Convert back to degrees for orientation
        self.alpha_deg = math.degrees(new_alpha_rad) % 360


    def update_vehicle_position(self,arduino, angle, speed):
            
        # Calculate the arc_length based on the time elapsed since last time
        new_time_stamp = time.time()
        duration = new_time_stamp - self.time_stamp
        self.time_stamp = new_time_stamp
        arc_length = duration * self.mm_per_step * self.old_speed # Assuming speed is slow and constant
        self.old_speed = speed

        # Calculate the rotation radius based on the previous direction
        radius = self.calculate_radius(self.old_direction_deg - 88)
        #print("Old_dir_deg = ", self.old_direction_deg)
        #print("Arc, radius = ", arc_length, radius)

        # Update old_direction_deg for next time
        self.old_direction_deg = angle

        # Calculate the new position and orientation
        self.move_along_arc(radius, arc_length)

    def update_data(self, arduino):
        for i in range (0, 10):

            # Remember the previous direction to eventually compute the new vehicle position based on distance travelled
            direction_deg = self.direction_speed_list[i][0]
            
            speed = self.direction_speed_list[i][1]
            self.set_direction_and_speed(direction_deg, speed)
            
            time.sleep (.5)
            self.update_vehicle_position(arduino, direction_deg, speed)
        
            #print(f"x, y, angle = {self.x:.0f} {self.y:.0f} {self.alpha_deg:.0f}")
            self.x_data.append(self.x)
            self.y_data.append(self.y)

    def update(self,frame):
        if self.x_data and self.y_data:
            self.line.set_data(self.x_data, self.y_data)
            #print("x_data = ", self.x_data)
            self.ax.relim()
            self.ax.autoscale_view()
        return self.line,


if __name__== '__main__':
    
    map_plotter = MapPlotter()

    #positions = []

    # Microstepping can be modified by software on Arduino
    microstepping =                     MICROSTEP_ONE_QUARTER # ***** still harcoded on Arduino

    # Connect to Arduino using USB
    arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    
    # Wait 2 seconds to let the communication link activate
    time.sleep(2)
 
    # Calculate the mm_per_step
    map_plotter.calculate_mm_per_step(microstepping)

    # Instead of fixed value, direction would be computed by vision
    data_thread = threading.Thread(target=map_plotter.update_data, args=(arduino,), daemon=True)

    data_thread.start()
    
    ani = animation.FuncAnimation(map_plotter.fig, map_plotter.update, interval = 100)


    
    plt.show()
    print("x,y = ", map_plotter.x, map_plotter.y)
    print("mm_per_step = ", map_plotter.mm_per_step)


    