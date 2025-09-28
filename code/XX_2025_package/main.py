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
from XX_2025_package.utils.enums import StartPosition
from XX_2025_package.utils.image_drawing_utils import ImageDrawingUtils

MOVE_TO_FRONT_ZONE = 2700
stop_run = False
allow_stop_run = False

arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)

# 0.1559 mm per 1 step
# 1 mm per 6.412 steps

if __name__ == "__main__":
    camera_manager = CameraManager()
    while True: # main loop to allow multiple runs without restarting
        ## 0 ##
        # Initialize program, camera, etc
        context_manager = ContextManager()
        lap_tracker = LapTracker(context_manager)
        image_algorithms = ImageAlgorithms(context_manager, camera_manager)
        camera_manager.start_camera()
        command = f"10000000!".encode()
        arduino.write(command)
        arduino.flush()

        ## 1 ##
        # Wait for start button to be pressed
        while True:
            if arduino.in_waiting > 0:
                data = arduino.read().decode('utf-8')
                if data == '1':
                    context_manager.set_challenge(1)
                    print("Challenge 1 selected")
                    break
                    
                elif data == '2':
                    context_manager.set_challenge(2)
                    print("Challenge 2 selected")
                    break

                elif data == '0':
                    print("0")
                    # only check after at least one run, so program isnt accidentally stopped before first attempt
                    if (allow_stop_run):
                        stop_run = True
                        break
                time.sleep(0.005)

        if stop_run:
            break
        allow_stop_run = True
        time.sleep(1)
        camera_manager.capture_image()
        camera_manager.transform_image()

        ################################################################
        ############################ Défi 1 ############################
        ################################################################
        
        if (ContextManager.CHALLENGE == 1):
            check_corner_flag = False
            start_time = 0
            speed = 5500

            # 1. Find direction with blue and orange lines
            image_algorithms.get_direction_from_lines()
            print("Direction : ", context_manager.get_direction())

            # 2. Find starting area
            start_position = image_algorithms.get_starting_position()
            print("Start position: ", start_position)
            context_manager.set_start_position(start_position)

            # 3. Complete 3 laps
            while True:
                camera_manager.capture_image()
                camera_manager.transform_image()
                lap_tracker.process_image(camera_manager.cnt_blueline, camera_manager.cnt_orangeline)
                angle, is_corner = image_algorithms.calculate_servo_angle_from_walls()
                command = f"m{angle},{speed}.".encode()
                arduino.write(command)
                arduino.flush()
                ImageDrawingUtils.add_text_to_image(camera_manager.display_image, f"Lap: {context_manager.get_lap_count()}", (10, 30), (0, 0, 255))
                camera_manager.add_frame_to_video()
                cv2.imshow("Display", camera_manager.display_image)

                # 4. Check last corner and stop the robot in the correct zone
                if (context_manager.is_last_quarter() or context_manager.has_completed_laps()):
                    speed = 4000
                    if start_time == 0:
                        start_time = time.time()
                    if (time.time() - start_time >= 1) and is_corner and not check_corner_flag:
                        print("Corner !")
                        check_corner_flag = True
                        final_corner_position = image_algorithms.check_last_corner_position()
                        print("Here's the final corner ! The outside wall is : ", final_corner_position)
                        # Add extra_move based on start position
                        if context_manager.get_start_position() == StartPosition.FRONT:
                            extra_move = MOVE_TO_FRONT_ZONE
                        else:
                            extra_move = 0
                        # Adjust move based on final corner position
                        if final_corner_position == 'C':
                            command = f"{6900}!".encode()
                            arduino.write(command)
                            speed = 1500
                        else:
                            command = f"{4400}!".encode()
                            arduino.write(command)
                            speed = 1500
                if arduino.in_waiting > 0:
                    if context_manager.has_completed_laps():
                        if arduino.read().decode('utf-8') == 'F':
                            break
                        time.sleep(0.005)
                # Let OpenCV update the window
                key = cv2.waitKey(1)  
                # Press escape key to quit (when testing)
                if key == 27:
                    if (speed != 0):
                        speed = 0
                    else:
                        break

        ################################################################
        ############################ Défi 2 ############################
        ################################################################
        # This comment is to test a git push bug we're facing
        if (ContextManager.CHALLENGE == 2):
            arduino.write(b"10000000!")
            speed = 3000
            
            ## 1 ##
            # Find direction with parking
            image_algorithms.get_direction_from_parking(camera_manager)
            print("Direction : ", context_manager.get_direction())
            ## 2 ##
            # Analyze starting area (optional)
            # Leave parking spot
            if context_manager.get_direction() == Direction.LEFT:
                command = f"t120,{speed},1200.".encode()
                arduino.write(command)
            else:
                print("Move right")
                command = f"t50,{speed},1200.".encode()
                arduino.write(command)
            print("Wait to complete")
            while arduino.read().decode('utf-8') != 'F':
                time.sleep(0.005)
            command = f"t85,{speed},1000.".encode()
            arduino.write(command)
            while arduino.read().decode('utf-8') != 'F':
                time.sleep(0.005)
            print("Complete")
            ## 3 ##
            # Complete 3 laps
            arduino.write(b"10000000!")
            while True:
                camera_manager.capture_image()
                camera_manager.transform_image()
                lap_tracker.process_image(camera_manager.cnt_blueline, camera_manager.cnt_orangeline)
                angle, is_green, _, _ = image_algorithms.find_obstacle_angle_and_draw_lines()
                if camera_manager.display_image is not None:
                    ImageDrawingUtils.add_text_to_image(camera_manager.display_image, f"Lap: {context_manager.get_lap_count()}", (10, 30), (0, 0, 255))
                    cv2.imshow("Display_image", camera_manager.display_image)
                #print("Angle objet : ", angle)
                angle_walls, _ = image_algorithms.calculate_servo_angle_from_walls()
                angle_obstacles = image_algorithms.calculate_servo_angle_from_obstacle(angle, is_green)
                servo_angle = image_algorithms.choose_output_angle(angle_walls, angle_obstacles)

                command = f"m{servo_angle},{speed}.".encode()
                arduino.write(command)
                arduino.flush()
                
                camera_manager.add_frame_to_video()

                cv2.imshow("Polygon Image", camera_manager.polygon_image)
                cv2.imshow("Blue Lines", camera_manager.cnt_blueline)
                cv2.imshow("Orange Lines", camera_manager.cnt_orangeline)
                cv2.imshow("Obstacle Image", camera_manager.obstacle_image)
                cv2.imshow("Pink Obstacle Image", camera_manager.pink_mask)
            

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

            last_color = image_algorithms.last_color
                
        ################################################################
        ############################ Défi 3 et 4 #######################
        ################################################################
        
        if (ContextManager.CHALLENGE == 2):
            arduino.write(b"10000000!")
            print("Going to parking")
            speed = 2000
            ## 1 ##
            print("Direction : ", context_manager.get_direction())
            pink_pixel_y = ImageTransformUtils.PIC_HEIGHT - 10
            pink_pixel_backwards_y = ImageTransformUtils.PIC_HEIGHT - 10
            if context_manager.get_direction() == Direction.LEFT:
                pink_pixel_x = ImageTransformUtils.PIC_WIDTH - 200
                pink_pixel_backwards_x = ImageTransformUtils.PIC_WIDTH - 100
            else:
                pink_pixel_x = 200
                pink_pixel_backwards_x = 100
            
            ## 4 ##
            # Approach the parking area (test)
            while True:
                camera_manager.capture_image()
                camera_manager.transform_image() 
                angle, is_green, obstacle_x, obstacle_y = image_algorithms.find_obstacle_angle_and_draw_lines()
                angle_pink, pink_x, pink_y, side = image_algorithms.find_pink_obstacle_angle()
                cv2.imshow("Obstacle Image", camera_manager.obstacle_image)
                cv2.imshow("Pink obstacle image", camera_manager.pink_mask)
                is_pink = 0
                if angle_pink is not None and pink_y is not None:
                    if obstacle_y is not None:
                        if (pink_y + 5) > obstacle_y:
                            angle = angle_pink
                            is_green = side
                            is_pink = 1
                            speed = 2000
                    else:
                        angle = angle_pink
                        is_green = side
                        speed = 2000
                angle_obstacles = image_algorithms.calculate_servo_angle_from_obstacle(angle, is_green)
                if camera_manager.display_image is not None:
                    cv2.imshow("Display_image", camera_manager.display_image)
                angle_walls, _ = image_algorithms.calculate_servo_angle_from_walls()
                servo_angle = image_algorithms.choose_output_angle(angle_walls, angle_obstacles)
                ImageDrawingUtils.draw_circle(camera_manager.display_image, (pink_pixel_x, pink_pixel_y), 5, (255, 0, 255))
                command = f"m{servo_angle},{speed}.".encode()
                arduino.write(command)
                arduino.flush()
                
                camera_manager.add_frame_to_video()
                if pink_x is not None and pink_y is not None:
                    if (context_manager.get_direction() == Direction.RIGHT and pink_x < 150 and pink_y > ImageTransformUtils.PIC_HEIGHT - 100) or (context_manager.get_direction() == Direction.LEFT and pink_x > ImageTransformUtils.PIC_WIDTH - 150 and pink_y > ImageTransformUtils.PIC_HEIGHT - 100):
                        break
                key = cv2.waitKey(1)  # Let OpenCV update the window
                if key == 27:  # Escape key to quit
                    break
            command = f"m85,0.".encode()
            arduino.write(command)

            ## 5 ##
            # Parallel park in the parking area
            print("Challenge 3")
            speed = 1000
            arduino.write(b"2000!")
            arduino_flag = False
            if context_manager.get_direction() == Direction.LEFT:
                context_manager.set_direction(Direction.RIGHT)
            else:
                context_manager.set_direction(Direction.LEFT)
                good_to_check = False
            while True:
                camera_manager.capture_image()
                camera_manager.transform_image()
                cv2.imshow("Cropped", camera_manager.cropped_image)
                cv2.imshow("Polygon Image", camera_manager.polygon_image)
                #print("Poly Lines = ", camera_manager.polygon_lines)
                angle_walls, _ = image_algorithms.calculate_servo_angle_from_walls(True)
                #print ("angle_walls = ", angle_walls)
                top_angle = image_algorithms.get_top_line_angle()
                #print("Top angle = ", top_angle)
                if arduino.in_waiting > 0:
                    if arduino.read().decode('utf-8') == 'F':
                        print("Done")
                        arduino.write(b"10000000!")
                        arduino_flag = True
                if (arduino_flag and camera_manager.binary_image[140, ImageTransformUtils.PIC_WIDTH // 2] == 0 and top_angle is not None and context_manager.get_direction() == Direction.RIGHT) or (arduino_flag and np.any(camera_manager.cnt_orangeline[ImageTransformUtils.PIC_HEIGHT - 100: ImageTransformUtils.PIC_HEIGHT - 65, ImageTransformUtils.PIC_WIDTH // 2 - 20: ImageTransformUtils.PIC_WIDTH // 2 + 20]) and context_manager.get_direction() == Direction.LEFT):
                    speed = 0
                    command = f"m85,0.".encode()
                    arduino.write(command)
                    break
                #else:
                #    speed = 1000
                command = f"m{angle_walls},{speed}.".encode()
                
                camera_manager.add_frame_to_video()
                arduino.write(command)
                arduino.flush()
            
                time.sleep(0.01)
                key = cv2.waitKey(1)  # Let OpenCV update the window
                if key == 27:  # Escape key to quit
                    if (speed != 0):
                        speed = 0
                    else:
                        break

            arduino.write(b"-10000000!")
            # Back up until pink wall is detected
            while True:
                camera_manager.capture_image()
                camera_manager.transform_image()
                cv2.imshow("Cropped", camera_manager.cropped_image)
                cv2.imshow("Polygon Image", camera_manager.polygon_image)
                if camera_manager.binary_image[pink_pixel_backwards_y, pink_pixel_backwards_x] == 0:
                    command = f"m85,0.".encode()
                    arduino.write(command)
                    break
                command = f"m85,-1000.".encode()
                arduino.write(command)
            time.sleep(0.2)

            #speed = 1000
            # Move forward a bit to prepare to enter the parking spot            
            command = f"t85,1000,{1850}.".encode()
            arduino.write(command)
            while arduino.read().decode('utf-8') != 'F':
                time.sleep(0.005)
            print(context_manager.get_direction())
            # Enter the parking spot while turning
            if (context_manager.get_direction() == Direction.LEFT and last_color == 1) or (context_manager.get_direction() == Direction.RIGHT and last_color == 0):
                print("Too close, turn less")
                command = f"t{87 - context_manager.get_direction().value * 37},-1000,1300.".encode()
            else:
                print("Normal")
                command = f"t{87 - context_manager.get_direction().value * 37},-1000,1400.".encode()
            arduino.write(command)
            while arduino.read().decode('utf-8') != 'F':
                time.sleep(0.005)
            # Backup straight inside the parking spot
            command = f"t85,-1000,675.".encode()
            arduino.write(command)
            while arduino.read().decode('utf-8') != 'F':
                time.sleep(0.005)
            # Backup while turning to straighten the robot
            command = f"t{87 + context_manager.get_direction().value * 37},-1000,1275.".encode()
            arduino.write(command)
            while arduino.read().decode('utf-8') != 'F':
                time.sleep(0.005)
            # Straighten the wheels
            command = f"m85,0.".encode()
            arduino.write(command)
        
        ################################################################
        #################### Code for movement tests ###################
        ################################################################
        if (ContextManager.CHALLENGE == 5):
            while True:
                command = f"t85,1000,10000.".encode()
                arduino.write(command)
                while arduino.read().decode('utf-8') != 'F':
                    time.sleep(0.005)
                command = f"t85,-1000,10000.".encode()
                arduino.write(command)
                while arduino.read().decode('utf-8') != 'F':
                    time.sleep(0.005)
        cv2.destroyAllWindows()
        arduino.write(b'm85,0.')