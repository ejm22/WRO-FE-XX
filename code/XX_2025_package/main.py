import cv2
import serial
import time
from XX_2025_package.classes.camera_manager import CameraManager
from XX_2025_package.utils.image_transform_utils import ImageTransformUtils
from XX_2025_package.classes.image_algoriths import ImageAlgorithms
from XX_2025_package.classes.context_manager import ContextManager
from XX_2025_package.classes.lap_tracker import LapTracker

arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)
speed = 3000

# 0.1559 mm per 1 step
# 1 mm per 6.412 steps

if __name__ == "__main__":
    ## 0 ##
    # Initialize program, camera, etc

    context_manager = ContextManager()
    lap_tracker = LapTracker(context_manager)
    
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
    
    if (ContextManager.challenge == 1):
        ## 1 ##
        # Find direction with blue and orange lines

        context_manager.set_direction(ImageAlgorithms.get_direction_from_lines(camera_manager))
        print("Direction : ", context_manager.get_direction())
        print(ImageAlgorithms.direction)

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
            lap_tracker.process_image(camera_manager.blueline_image, camera_manager.orangeline_image)
            cv2.imshow("Cropped", camera_manager.cropped_image)
            cv2.imshow("New Image", camera_manager.polygon_image)
            if arduino.out_waiting == 0:
                angle = ImageAlgorithms.calculate_servo_angle_walls(camera_manager.polygon_image)
                command = f"m{angle},{speed}.".encode()
                arduino.write(command)
                arduino.flush()
            else:
                print("Arduino is busy, skipping command.")
            time.sleep(0.01)

            if (context_manager.has_completed_laps()):
                break

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

    if (ContextManager.challenge == 2):
        ## 1 ##
        # Find direction with parking

        ## 2 ##
        # Analyze starting area (optional)

        ## 3 ##
        # Complete 3 laps
        context_manager.set_direction(ImageAlgorithms.get_direction_from_parking(camera_manager))
        print("Direction : ", context_manager.get_direction())
        time.sleep(4)
        while True:
            camera_manager.capture_image()
            camera_manager.transform_image()
            lap_tracker.process_image(camera_manager.hsv_image)
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
            cv2.imshow("blue line", camera_manager.cnt_blueline)
            cv2.imshow("orange line", camera_manager.cnt_orangeline)
            #cv2.imshow("Polygon image", camera_manager.polygon_image)
            #cv2.imshow("Cropped image", camera_manager.cropped_image)
            #cv2.imshow("Lol", camera_manager.obstacle_image)
            cv2.imshow("Binary image", camera_manager.binary_image)
            cv2.imshow("Obstacle with rect", camera_manager.contour_obstacle_with_rect)
            #cv2.imshow("Pink image", camera_manager.pink_image)
            command = f"m{servo_angle},{speed}.".encode()
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

    if (ContextManager.challenge == 3):
       
        print("Challenge 3")
        while True:
            speed = 1000
            while True:
                arduino.flushInput()
                camera_manager.capture_image()
                camera_manager.transform_image()

                cv2.imshow("Cropped", camera_manager.cropped_image)
                cv2.imshow("Polygon Image", camera_manager.polygon_image)
                #print("Poly Lines = ", camera_manager.polygon_lines)
                angle_walls = ImageAlgorithms.calculate_servo_angle_walls(camera_manager.polygon_image)
                print ("angle_walls = ", angle_walls)
                top_angle = ImageAlgorithms.get_top_angle(camera_manager.polygon_lines)
                #print("Top angle = ", top_angle)
                #servo_angle = ImageAlgorithms.calculate_servo_angle_parking(angle_walls, top_angle)

                #command = f"{servo_angle},{speed}.".encode()
                if camera_manager.binary_image[85, ImageTransformUtils.PIC_WIDTH // 2] == 0 and top_angle is not None:
                    speed = 0
                    command = f"m85,0.".encode()
                    arduino.write(command)
                    break
                else:
                    speed = 1000
                command = f"m{angle_walls},{speed}.".encode()
                

                arduino.write(command)
                arduino.flush()
            
                time.sleep(0.01)
                key = cv2.waitKey(1)  # Let OpenCV update the window
                if key == 27:  # Escape key to quit
                    if (speed != 0):
                        speed = 0
                    else:
                        break
            
            while True:
                camera_manager.capture_image()
                camera_manager.transform_image()
                cv2.imshow("Cropped", camera_manager.cropped_image)
                cv2.imshow("Polygon Image", camera_manager.polygon_image)
                if camera_manager.binary_image[ImageTransformUtils.PIC_HEIGHT - 10, ImageTransformUtils.PIC_WIDTH - 100] == 0:
                    command = f"m85,0.".encode()
                    arduino.write(command)
                    break
                command = f"m85,-1000.".encode()
                arduino.write(command)
            time.sleep(0.2)

            speed = 1000
            command = f"t85,1000,1750.".encode()
            arduino.write(command)
            time.sleep(3)
            
            command = f"t48,-1000,1350.".encode()
            arduino.write(command)
            time.sleep (7)
            command = f"t85,-1000,650.".encode()
            arduino.write(command)
            time.sleep (1.5)
            command = f"t128,-1000,1300.".encode()
            arduino.write(command)
            time.sleep (1.5)
            command = f"m85,0.".encode()
            arduino.write(command)
            
            break
            
    if (ContextManager.challenge == 4):
        print("Hello")
        command = f"t48,-1000,-1500.".encode()
        arduino.write(command)
        time.sleep (1.8)
        command = f"t85,-1000,-1100.".encode()
        arduino.write(command)
        time.sleep (1.5)
        command = f"t128,-1000,-1300.".encode()
        arduino.write(command)
        time.sleep (1.5)
        command = f"m85,0.".encode()
        arduino.write(command)
 
    cv2.destroyAllWindows()
    arduino.write(b'm88,0.')