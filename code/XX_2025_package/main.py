import serial
import cv2
import time
import numpy as np
from classes.camera_manager import CameraManager
from utils.image_transform_utils import ImageTransformUtils
from classes.image_algoriths import ImageAlgorithms
from classes.context_manager import ContextManager
from classes.lap_tracker import LapTracker
from utils.enums import Direction
from utils.enums import StartPosition
from utils.image_drawing_utils import ImageDrawingUtils
from classes.arduino_comms import ArduinoComms

MOVE_TO_FRONT_ZONE = 2700
stop_run = False

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
        arduino = ArduinoComms()
        camera_manager.start_camera()
        arduino.send('!', 10000000)

        # Run the image analysis once to initialize variables
        camera_manager.capture_image()
        camera_manager.transform_image()

        ## 1 ##
        # Wait for start button to be pressed
        while True:
            msg = arduino.read()
            if msg:
                if msg == '1':
                    context_manager.set_challenge(1)
                    print("Challenge 1 selected")
                    break
                    
                elif msg == '2':
                    context_manager.set_challenge(2)
                    print("Challenge 2 selected")
                    break

                elif msg == '0':
                    print("Leave program")
                    stop_run = True
                    break
                time.sleep(0.005)

        if stop_run:
            break
        #time.sleep(1)
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
                arduino.send('m', angle, speed)
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
                            arduino.send('!', 6900)
                            speed = 1500
                        else:
                            arduino.send('!', 4400)
                            speed = 1500
                if context_manager.has_completed_laps() and arduino.read() == 'F':
                    break
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
            arduino.send('!', 10000000)
            speed = 3500
            
            ## 1 ##
            # Find direction with parking
            image_algorithms.get_direction_from_parking(camera_manager)
            print("Direction : ", context_manager.get_direction())
            
            ## 2 ##
            # Analyze starting area (optional)
            # Leave parking spot
            if context_manager.get_direction() == Direction.LEFT:
                arduino.send('t', 120, speed, 1200)
            else:
                print("Move right")
                arduino.send('t', 50, speed, 1200)
            
            #arduino.send('t', 85, speed, 1000)
            arduino.send('!', 10000000)
            arduino.send('m', 85, speed)
            time.sleep(1.0)
        
            ## 3 ##
            # Complete 3 laps
            while True:
                camera_manager.capture_image()
                camera_manager.transform_image()
                lap_tracker.process_image(camera_manager.cnt_blueline, camera_manager.cnt_orangeline)
                angle, is_green, _, y_center = image_algorithms.find_obstacle_angle_and_draw_lines()
                
                accel_decel = True
                #########################################
                # Accelerate/decelerate if object is far enough
                if accel_decel:
                    if y_center is not None:
                        if y_center < 130:
                            speed = 4200 # 4200 for max speed
                        else:
                            speed = 3500
                    else:
                        speed = 3500
                #########################################

                if camera_manager.display_image is not None:
                    ImageDrawingUtils.add_text_to_image(camera_manager.display_image, f"Lap: {context_manager.get_lap_count()}", (10, 30), (0, 0, 255))
                    cv2.imshow("Display_image", camera_manager.display_image)
                #print("Angle objet : ", angle)
                angle_walls, _ = image_algorithms.calculate_servo_angle_from_walls()
                angle_obstacles = image_algorithms.calculate_servo_angle_from_obstacle(angle, is_green)
                servo_angle = image_algorithms.choose_output_angle(angle_walls, angle_obstacles)

                arduino.send('m', servo_angle, speed)

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
            arduino.send('!', 10000000)
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

            # Set the last obstacle seen after 3rd lap default value
            # Objective is to detect if a red pillar is seen last when going left and green when going right
            if context_manager.get_direction() == Direction.LEFT:
                last_was_green = True
            else:
                last_was_green = False

            while True:
                camera_manager.capture_image()
                camera_manager.transform_image() 
                angle, is_green, obstacle_x, obstacle_y = image_algorithms.find_obstacle_angle_and_draw_lines()
                angle_pink, pink_x, pink_y, side = image_algorithms.find_pink_obstacle_angle()
                cv2.imshow("Obstacle Image", camera_manager.obstacle_image)
                cv2.imshow("Pink obstacle image", camera_manager.pink_mask)
                is_pink = 0

                #########################################################
                # Determine the last obstacle color seen after 3rd lap
                if obstacle_y is not None:
                    if obstacle_y > 175:  # Only consider obstacle if it's close
                        last_was_green = is_green
                        print("Last was green after 3rd lap:", last_was_green)
                #########################################################   
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
                arduino.send('m', servo_angle, speed)
                camera_manager.add_frame_to_video()
                if pink_x is not None and pink_y is not None:
                    if (context_manager.get_direction() == Direction.RIGHT and pink_x < 150 and pink_y > ImageTransformUtils.PIC_HEIGHT - 100) or (context_manager.get_direction() == Direction.LEFT and pink_x > ImageTransformUtils.PIC_WIDTH - 150 and pink_y > ImageTransformUtils.PIC_HEIGHT - 100):
                        break
                key = cv2.waitKey(1)  # Let OpenCV update the window
                if key == 27:  # Escape key to quit
                    break
            arduino.send('m', 85, 0)

            ## 5 ##
            # Parallel park in the parking area
            print("Challenge 3")
            speed = 1000
            arduino.send('!', 2000)
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
                if arduino.read() == 'F':
                    print("Done")
                    arduino.send('!', 10000000)
                    arduino_flag = True
                if (arduino_flag and camera_manager.binary_image[140, ImageTransformUtils.PIC_WIDTH // 2] == 0 and top_angle is not None and context_manager.get_direction() == Direction.RIGHT) or (arduino_flag and np.any(camera_manager.cnt_orangeline[ImageTransformUtils.PIC_HEIGHT - 100: ImageTransformUtils.PIC_HEIGHT - 65, ImageTransformUtils.PIC_WIDTH // 2 - 20: ImageTransformUtils.PIC_WIDTH // 2 + 20]) and context_manager.get_direction() == Direction.LEFT):
                    speed = 0
                    arduino.send('m', 85, speed)
                    break
                #else:
                #    speed = 1000
                arduino.send('m', angle_walls, speed)
                camera_manager.add_frame_to_video()
            
                time.sleep(0.01)
                key = cv2.waitKey(1)  # Let OpenCV update the window
                if key == 27:  # Escape key to quit
                    if (speed != 0):
                        speed = 0
                    else:
                        break

            arduino.send('!', -10000000)
            speed = 2500 #2500 for faster parking

            # Back up a certain distance
            arduino.send('m', 85, -speed)
            time.sleep(2.4)
            # Back up until pink wall is detected
            while True:
                camera_manager.capture_image()
                camera_manager.transform_image()
                cv2.imshow("Cropped", camera_manager.cropped_image)
                cv2.imshow("Polygon Image", camera_manager.polygon_image)
                if camera_manager.binary_image[pink_pixel_backwards_y, pink_pixel_backwards_x] == 0:
                    arduino.send('m', 85, 0)
                    break
                arduino.send('m', 85, -1000)
            time.sleep(0.2)

            #speed = 1000
            # Move forward a bit to prepare to enter the parking spot
            arduino.send('!', 10000000)
            # arduino.send('t', 85, 1000, 1850)

            print(context_manager.get_direction())
            # Enter the parking spot while turning
            if (context_manager.get_direction() == Direction.LEFT and last_was_green) or (context_manager.get_direction() == Direction.RIGHT and not last_was_green):
                print("Too close, move forward less, turn less")
                arduino.send('t', 85, speed, 1750)
                arduino.send('t', 86 - context_manager.get_direction().value * 37, -speed, 1250)
            else:
                print("Normal")
                arduino.send('t', 85, speed, 1850)
                arduino.send('t', 86 - context_manager.get_direction().value * 37, -speed, 1400)
            
            # Backup straight inside the parking spot
            arduino.send('t', 85, -speed, 675)
            # Backup while turning to straighten the robot
            arduino.send('t', 86 + context_manager.get_direction().value * 37, -speed, 1250)
            # Straighten the wheels
            arduino.send('m', 85, 0)
        
        ################################################################
        #################### Code for movement tests ###################
        ################################################################
        if (ContextManager.CHALLENGE == 5):
            while True:
                arduino.send('t', 85, 1000, 10000)
                arduino.send('t', 85, -1000, 10000)
        cv2.destroyAllWindows()
        arduino.send('m', 85, 0)