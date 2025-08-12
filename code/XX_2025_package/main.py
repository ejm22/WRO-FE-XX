import cv2
import serial
import time
from XX_2025_package.classes.camera_manager import CameraManager
from XX_2025_package.utils.image_utils import ImageTransformUtils
from XX_2025_package.classes.image_algoriths import ImageAlgorithms
from XX_2025_package.classes.context_manager import ContextManager
from XX_2025_package.classes.lap_tracker import LapTracker

arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)
speed = 3000
defi = 2

if __name__ == "__main__":
    ## 0 ##
    # Initialize program, camera, etc

    context_manager = ContextManager()
    
    time.sleep(1)
    camera_manager = CameraManager()
    camera_manager.start_camera()
    arduino.write(b'v')
    time.sleep(0.1)
    line=arduino.readline().decode().strip()
    if line:
        print(line)
        level_text = line.replace("Battery voltage: ", "")
        level_value = float(level_text)
        if (level_value > 5) and (level_value < 11):
            print("BATTERY LOW")
            exit (1)

    camera_manager.capture_image()
    camera_manager.transform_image()

    ################################################################
    ############################ Défi 1 ############################
    ################################################################
    
    if (defi == 1):
        ## 1 ##
        # Find direction with blue and orange lines

        context_manager.set_direction(ImageAlgorithms.get_direction(camera_manager))
        print("Direction : ", context_manager.get_direction())

        ## 2 ##
        # Find starting area

        ## 2.1 ##
        # Adjust robot if starting area is problematic

        ## 3 ##
        # Complete 3 laps
        while True:
            arduino.flushInput()
            camera_manager.capture_image()
            camera_manager.transform_image()
            cv2.imshow("Cropped", camera_manager.cropped_image)
            cv2.imshow("New Image", camera_manager.polygon_image)
            if arduino.out_waiting == 0:
                angle = ImageAlgorithms.calculate_servo_angle_walls(camera_manager.polygon_image)
                command = f"{angle},{speed}.".encode()
                arduino.write(command)
                arduino.flush()
            else:
                print("Arduino is busy, skipping command.")
            time.sleep(0.01)
            key = cv2.waitKey(1)  # Let OpenCV update the window
            if key == 27:  # Escape key to quit
                if (speed != 0):
                    speed = 0
                else:
                    break


        ## 4 ##
        # Stop the robot in the correct zone

    ################################################################
    ############################ Défi 2 ############################
    ################################################################

    if (defi == 2):
        ## 1 ##
        # Find direction with parking

        ## 2 ##
        # Analyze starting area (optional)

        ## 3 ##
        # Complete 3 laps
        while True:
            camera_manager.capture_image()
            camera_manager.transform_image()
            display_image = camera_manager.cropped_image.copy()
            angle, display_image, is_green = ImageAlgorithms.find_obstacle_angle(camera_manager.obstacle_image.copy(), 
                                                               camera_manager.hsv_image.copy(), 
                                                               display_image, 
                                                               camera_manager.grayscale_image.copy())
            if display_image is not None:
                cv2.imshow("Display_image", display_image)
            print("Angle objet : ", angle)
            angle_walls = ImageAlgorithms.calculate_servo_angle_walls(camera_manager.polygon_image)
            angle_obstacles = ImageAlgorithms.calculate_servo_angle_obstacle(angle, is_green)
            servo_angle = ImageAlgorithms.choose_output_angle(angle_walls, angle_obstacles)
            print("angle_walls,angle_obstacles, servo_angle", angle_walls, angle_obstacles, servo_angle)

            #cv2.imshow("Polygon image", camera_manager.polygon_image)
            #cv2.imshow("Cropped image", camera_manager.cropped_image)
            #cv2.imshow("Lol", camera_manager.obstacle_image)
            cv2.imshow("Binary image", camera_manager.binary_image)
            cv2.imshow("Obstacle with rect", camera_manager.contour_obstacle_with_rect)
            #cv2.imshow("Pink image", camera_manager.pink_image)
            command = f"{servo_angle},{speed}.".encode()
            arduino.write(command)
            arduino.flush()
            time.sleep(0.01)
            key = cv2.waitKey(1)  # Let OpenCV update the window
            if key == 27:  # Escape key to quit
                break
        ## 4 ##
        # Approach the parking area

        ## 5 ##
        # Parallel park in the parking area

    if (defi == 3):
       
        print("Defi 3")
        speed = 500
        while True:
            arduino.flushInput()
            camera_manager.capture_image()
            camera_manager.transform_image()

            cv2.imshow("Cropped", camera_manager.cropped_image)
            cv2.imshow("Polygon Image", camera_manager.polygon_image)
            #print("Poly Lines = ", camera_manager.polygon_lines)
            angle_walls = ImageAlgorithms.calculate_servo_angle_walls(camera_manager.polygon_image)
            print ("angle_walls = ", angle_walls)
            wall_angle = ImageAlgorithms.get_facing_wall_angle(camera_manager.polygon_lines)
            print("Exterior wall angle = ", wall_angle)

            angle = ImageAlgorithms.calculate_servo_angle_walls(camera_manager.polygon_image)
            servo_angle = ImageAlgorithms.calculate_servo_angle_parking(angle_walls, wall_angle)

            #command = f"{servo_angle},{speed}.".encode()
            if camera_manager.binary_image[63, 320] == 0:
                speed = 0
            else:
                speed = 300
            command = f"{servo_angle},{speed}.".encode()
            

            arduino.write(command)
            arduino.flush()
        
            time.sleep(0.01)
            key = cv2.waitKey(1)  # Let OpenCV update the window
            if key == 27:  # Escape key to quit
                if (speed != 0):
                    speed = 0
                else:
                    break
           
        
    cv2.destroyAllWindows()
    arduino.write(b'88,0.')