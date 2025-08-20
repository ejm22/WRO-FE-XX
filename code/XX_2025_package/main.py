import serial
import cv2
import time
import numpy as np
from XX_2025_package.classes.camera_manager import CameraManager
from XX_2025_package.utils.image_transform_utils import ImageTransformUtils
from XX_2025_package.classes.image_algoriths import ImageAlgorithms
from XX_2025_package.classes.context_manager import ContextManager
from XX_2025_package.classes.lap_tracker import LapTracker
from XX_2025_package.utils.enums import Direction
from XX_2025_package.utils.image_drawing_utils import ImageDrawingUtils

arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)

# 0.1559 mm per 1 step
# 1 mm per 6.412 steps

if __name__ == "__main__":
    ## 0 ##
    # Initialize program, camera, etc

    context_manager = ContextManager()
    camera_manager = CameraManager()
    lap_tracker = LapTracker(context_manager)
    image_algorithms = ImageAlgorithms(context_manager, camera_manager)
    
    time.sleep(1)
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
    
    if (ContextManager.CHALLENGE == 1):
        speed = 5000
        ## 1 ##
        # Find direction with blue and orange lines

        image_algorithms.get_direction_from_lines(camera_manager)
        print("Direction : ", context_manager.get_direction())

        ## 2 ##
        # Find starting area
        start_position = image_algorithms.get_starting_position(camera_manager.polygon_image)
        print("Start position: ", start_position)
        context_manager.set_start_position(start_position)

        ## 3 ##
        # Complete 3 laps
        while True:
            arduino.flushInput()
            camera_manager.capture_image()
            camera_manager.transform_image()
            lap_tracker.process_image(camera_manager.cnt_blueline, camera_manager.cnt_orangeline)
            cv2.imshow("Cropped", camera_manager.cropped_image)
            cv2.imshow("New Image", camera_manager.polygon_image)
            if arduino.out_waiting == 0:
                angle = image_algorithms.calculate_servo_angle_from_walls(camera_manager.polygon_image)
                command = f"m{angle},{speed}.".encode()
                arduino.write(command)
                arduino.flush()
            else:
                print("Arduino is busy, skipping command.")
            
            camera_manager.display_image = camera_manager.polygon_image.copy()
            ImageDrawingUtils.add_text_to_image(camera_manager.display_image, f"Lap: {lap_tracker.get_lap_count()}", (10, 30), (0, 0, 255), 1)
            camera_manager.add_frame_to_video()
                        

            if context_manager.has_completed_laps() and image_algorithms.get_back_wall_distance() > ImageTransformUtils.START_WALL_HEIGHT_THRESHOLD:
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

    if (ContextManager.CHALLENGE == 2):
        speed = 3000
        ## 1 ##
        # Find direction with parking
        image_algorithms.get_direction_from_parking(camera_manager)
        print("Direction : ", context_manager.get_direction())
        ## 2 ##
        # Analyze starting area (optional)
        # Leave parking spot

        ## 3 ##
        # Complete 3 laps
        while True:
            camera_manager.capture_image()
            camera_manager.transform_image()
            lap_tracker.process_image(camera_manager.cnt_blueline, camera_manager.cnt_orangeline)
            angle, camera_manager.display_image, is_green, _, _ = image_algorithms.find_obstacle_angle_and_draw_lines(camera_manager.display_image)
            if camera_manager.display_image is not None:
                ImageDrawingUtils.add_text_to_image(camera_manager.display_image, f"Lap: {lap_tracker.get_lap_count()}", (10, 30), (0, 0, 255), 1)
                cv2.imshow("Display_image", camera_manager.display_image)
            #print("Angle objet : ", angle)
            angle_walls = image_algorithms.calculate_servo_angle_from_walls(camera_manager.polygon_image)
            angle_obstacles = image_algorithms.calculate_servo_angle_from_obstacle(angle, is_green)
            servo_angle = image_algorithms.choose_output_angle(angle_walls, angle_obstacles)

            command = f"m{servo_angle},{speed}.".encode()
            arduino.write(command)
            arduino.flush()
            
            camera_manager.add_frame_to_video()
            
            time.sleep(0.01)

            if (context_manager.has_completed_laps()):
                break

            key = cv2.waitKey(1)  # Let OpenCV update the window
            if key == 27:  # Escape key to quit
                break
        ## 4 ##
        # Approach the parking area

        ## 5 ##
        # Parallel park in the parking area

    if (ContextManager.CHALLENGE == 3):
       
        print("Challenge 3")
        while True:
            speed = 1000
            while True:
                arduino.flushInput()
                camera_manager.capture_image()
                camera_manager.transform_image()
                context_manager.set_direction(Direction.RIGHT)
                cv2.imshow("Cropped", camera_manager.cropped_image)
                cv2.imshow("Polygon Image", camera_manager.polygon_image)
                #print("Poly Lines = ", camera_manager.polygon_lines)
                angle_walls = image_algorithms.calculate_servo_angle_from_walls(camera_manager.polygon_image)
                #print ("angle_walls = ", angle_walls)
                top_angle = image_algorithms.get_top_line_angle(camera_manager.polygon_lines)
                #print("Top angle = ", top_angle)
                #servo_angle = ImageAlgorithms.calculate_servo_angle_parking(angle_walls, top_angle)

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
            while arduino.read().decode('utf-8') != 'F':
                time.sleep(0.005)
            command = f"t48,-1000,1350.".encode()
            arduino.write(command)
            while arduino.read().decode('utf-8') != 'F':
                time.sleep(0.005)
            command = f"t85,-1000,650.".encode()
            arduino.write(command)
            while arduino.read().decode('utf-8') != 'F':
                time.sleep(0.005)
            command = f"t128,-1000,1300.".encode()
            arduino.write(command)
            while arduino.read().decode('utf-8') != 'F':
                time.sleep(0.005)
            command = f"m85,0.".encode()
            arduino.write(command)
            
            break
            
    if (ContextManager.CHALLENGE == 4):
        print("Hello")
        speed = 3000
        ## 1 ##
        # Find direction with parking
        image_algorithms.get_direction_from_parking(camera_manager)
        print("Direction : ", context_manager.get_direction())
        pink_pixel_y = ImageTransformUtils.PIC_HEIGHT - 80
        if context_manager.get_direction() == Direction.LEFT:
            pink_pixel_x = ImageTransformUtils.PIC_WIDTH - 70
            pink_pixel_backwards_x = ImageTransformUtils.PIC_WIDTH - 100
        else:
            pink_pixel_x = 70
            pink_pixel_backwards_x = 100
            
        ## 2 ##
        # Analyze starting area (optional)
        # Leave parking spot

        ## 3 ##
        
        ## 4 ##
        # Approach the parking area 
        while True:
            camera_manager.capture_image()
            camera_manager.transform_image() 
            angle, camera_manager.display_image, is_green, obstacle_x, obstacle_y = image_algorithms.find_obstacle_angle_and_draw_lines(camera_manager.display_image)
            angle_pink, camera_manager.display_image, pink_x, pink_y, side = image_algorithms.find_pink_obstacle_angle(camera_manager.display_image)
            cv2.imshow("Obstacle Image", camera_manager.obstacle_image)
            cv2.imshow("Pink obstacle image", camera_manager.pink_mask)
            is_pink = 0
            if angle_pink is not None and pink_y is not None:
                if obstacle_y is not None:
                    if (pink_y + 5) > obstacle_y:
                        print("PINK 1")
                        angle = angle_pink
                        is_green = side
                        is_pink = 1
                        speed = 1500
                else:
                    print("PINK 2")
                    angle = angle_pink
                    is_green = side
                    is_pink = 1
                    speed = 1500
            angle_obstacles = image_algorithms.calculate_servo_angle_from_obstacle(angle, is_green, is_pink)
            if camera_manager.display_image is not None:
                cv2.imshow("Display_image", camera_manager.display_image)
            angle_walls = image_algorithms.calculate_servo_angle_from_walls(camera_manager.polygon_image)
            servo_angle = image_algorithms.choose_output_angle(angle_walls, angle_obstacles)

            command = f"m{servo_angle},{speed}.".encode()
            arduino.write(command)
            arduino.flush()
            
            camera_manager.add_frame_to_video()

            if camera_manager.pink_mask[pink_pixel_y, pink_pixel_x] == 255:
                break
            key = cv2.waitKey(1)  # Let OpenCV update the window
            if key == 27:  # Escape key to quit
                break
        command = f"m86,0.".encode()
        arduino.write(command)

        ## 5 ##
        # Parallel park in the parking area
        print("Challenge 3")
        speed = 1000
        if context_manager.get_direction() == Direction.LEFT:
            context_manager.set_direction(Direction.RIGHT)
        else:
            context_manager.set_direction(Direction.LEFT)
            good_to_check = False
        while True:
            arduino.flushInput()
            camera_manager.capture_image()
            camera_manager.transform_image()
            cv2.imshow("Cropped", camera_manager.cropped_image)
            cv2.imshow("Polygon Image", camera_manager.polygon_image)
            #print("Poly Lines = ", camera_manager.polygon_lines)
            angle_walls = image_algorithms.calculate_servo_angle_from_walls(camera_manager.polygon_image, True)
            #print ("angle_walls = ", angle_walls)
            top_angle = image_algorithms.get_top_line_angle(camera_manager.polygon_lines)
            #print("Top angle = ", top_angle)
            #servo_angle = ImageAlgorithms.calculate_servo_angle_parking(angle_walls, top_angle)

            if np.any(camera_manager.cnt_orangeline[ImageTransformUtils.PIC_HEIGHT - 165: ImageTransformUtils.PIC_HEIGHT - 140, ImageTransformUtils.PIC_WIDTH // 2 - 20: ImageTransformUtils.PIC_WIDTH // 2 + 20]):
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
            if camera_manager.binary_image[ImageTransformUtils.PIC_HEIGHT - 10, pink_pixel_backwards_x] == 0:
                command = f"m85,0.".encode()
                arduino.write(command)
                break
            command = f"m85,-1000.".encode()
            arduino.write(command)
        time.sleep(0.2)

        speed = 1000
        command = f"t85,1000,1700.".encode()
        arduino.write(command)
        while arduino.read().decode('utf-8') != 'F':
            time.sleep(0.005)
        command = f"t{85 - context_manager.get_direction().value * 37},-1000,1300.".encode()
        arduino.write(command)
        while arduino.read().decode('utf-8') != 'F':
            time.sleep(0.005)
        command = f"t85,-1000,650.".encode()
        arduino.write(command)
        while arduino.read().decode('utf-8') != 'F':
            time.sleep(0.005)
        command = f"t{85 + context_manager.get_direction().value * 37},-1000,1200.".encode()
        arduino.write(command)
        while arduino.read().decode('utf-8') != 'F':
            time.sleep(0.005)
        command = f"m85,0.".encode()
        arduino.write(command)

    cv2.destroyAllWindows()
    arduino.write(b'm88,0.')