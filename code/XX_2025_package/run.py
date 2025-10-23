# region Imports
import cv2
import time
import numpy as np
# Classes
from classes.camera_manager import CameraManager
from classes.image_algoriths import ImageAlgorithms
from classes.context_manager import ContextManager
from classes.lap_tracker import LapTracker
from classes.arduino_comms import ArduinoComms
from classes.info_overlay_processor import InfoOverlayProcessor
from classes.video_thread import VideoThread
# Utils
from utils.image_transform_utils import ImageTransformUtils
from utils.enums import Direction
from utils.image_drawing_utils import ImageDrawingUtils
from utils.enums import RunStates
from utils.debug_timer import DebugTimer
# endregion Imports

# region Constants
ANGLE_STRAIGHT = 85
SPEED_STOP = 0
SPEED_CHALLENGE_1_FAST = 5500
SPEED_CHALLENGE_1_MID = 4000
SPEED_CHALLENGE_1_SLOW = 1500
SPEED_CHALLENGE_2_OBSTACLES = 4200
SPEED_CHALLENGE_2_WALLS = 3500
SPEED_CHALLENGE_2_APPROACH = 2000
SPEED_CHALLENGE_2_PARKING = 1000
SPEED_CHALLENGE_2_ACCELERATED_PARKING = 2500
OBJECT_FAR_ENOUGH = 130
OBJECT_CLOSE_ENOUGH = 175
# endregion Constants

# Run
if __name__ == "__main__":
    state = RunStates.INITIALIZATIONS
    speed = 0
    camera_manager = CameraManager()
    
    try:
        # Main loop
        while True:
            
            # region State 0 : Initializations
            if state == RunStates.INITIALIZATIONS:
                context_manager = ContextManager()
                info_overlay_processor = InfoOverlayProcessor(context_manager, camera_manager)
                lap_tracker = LapTracker(context_manager)
                image_algorithms = ImageAlgorithms(context_manager, camera_manager)
                arduino = ArduinoComms()
                debug_timer = DebugTimer()
                camera_manager.start_camera()
                camera_manager.capture_image()
                camera_manager.transform_image()
                state = RunStates.WAIT_FOR_START
                check_corner_flag = False
                start_time = 0
                
                video_thread = VideoThread(camera_manager, context_manager, info_overlay_processor) 
                video_thread.start()
                #print('Thread state: ', video_thread.is_alive())

            # endregion State 0 : Initializations
            debug_timer.start("Main loop")
            # region State 1 : Wait for start
            if state == RunStates.WAIT_FOR_START:
                msg = arduino.read()
                if msg:
                    if msg == '1':
                        context_manager.set_challenge(1)
                        state = RunStates.CHALLENGE_1_FIND_DIRECTION
                        context_manager.start_timer()
                    elif msg == '2':
                        context_manager.set_challenge(2)
                        state = RunStates.CHALLENGE_2_FIND_DIRECTION
                        context_manager.start_timer()
                    elif msg == '0':
                        state = RunStates.STOP
                        break
                    time.sleep(0.005)
            # endregion State 1 : Wait for start

            # region To-do every loop
            if state is not RunStates.INITIALIZATIONS and state is not RunStates.WAIT_FOR_START:
                camera_manager.capture_image()
                camera_manager.transform_image()
                camera_manager.display_image = camera_manager.cropped_image.copy()
                lap_tracker.process_image(camera_manager.cnt_blueline, camera_manager.cnt_orangeline)
                context_manager.set_state(state)
            # endregion To-do end of every loop

            # region State 11 : Challenge 1 - Find Direction
            if state == RunStates.CHALLENGE_1_FIND_DIRECTION:
                arduino.send('!', 10000000)
                # Find direction
                image_algorithms.get_direction_from_lines()
                print("Direction: ", context_manager.get_direction())
                # Also, find starting area, because why not :)
                start_position = image_algorithms.get_starting_position()
                context_manager.set_start_position(start_position)
                print("Start position: ", start_position)
                speed = SPEED_CHALLENGE_1_FAST
                state = RunStates.CHALLENGE_1_LAPS
            # endregion State 11 : Challenge 1 - Find Direction

            # region State 12 : Challenge 1 - Laps
            if state == RunStates.CHALLENGE_1_LAPS:
                angle, is_corner = image_algorithms.calculate_servo_angle_from_walls()
                # Verify distance to travel to stop in the correct position
                if (context_manager.is_last_quarter()):
                    speed = SPEED_CHALLENGE_1_MID
                    start_time = time.time()
                    state = RunStates.CHALLENGE_1_PARKING
            # endregion State 12 : Challenge 1 - Laps

            # region State 13 : Challenge 1 - Parking
            if state == RunStates.CHALLENGE_1_PARKING:
                angle, is_corner = image_algorithms.calculate_servo_angle_from_walls()
                # 1 second after the corner was detected, reduce speed and set final move
                if (time.time() - start_time >= 1) and is_corner and not check_corner_flag:
                    check_corner_flag = True
                    final_corner_position = image_algorithms.check_last_corner_position()
                    # Insert here the code to add an extra move if we need to finish in the correct zone (SURPRISE RULE)
                    if final_corner_position == 'C':
                        arduino.send('!', 6900)
                    else:
                        arduino.send('!', 4400)
                    speed = SPEED_CHALLENGE_1_SLOW
                if context_manager.has_completed_laps() and arduino.read() == 'F':
                    state = RunStates.STOP
            # endregion State 13 : Challenge 1 - Parking

            # region State 21 : Challenge 2 - Find Direction
            if state == RunStates.CHALLENGE_2_FIND_DIRECTION:
                speed = SPEED_CHALLENGE_2_WALLS
                # Find direction
                image_algorithms.get_direction_from_parking(camera_manager)
                if context_manager.get_direction() == Direction.LEFT:
                    challenge_direction = Direction.LEFT
                    parking_direction = Direction.RIGHT
                else:
                    challenge_direction = Direction.RIGHT
                    parking_direction = Direction.LEFT
                # Leave parking spot
                arduino.send('t', ANGLE_STRAIGHT - 35 * challenge_direction.value, speed, 1200)
                arduino.send('!', 10000000)
                arduino.send('m', ANGLE_STRAIGHT, speed)
                time.sleep(0.9)
                state = RunStates.CHALLENGE_2_LAPS
            # endregion State 21 : Challenge 2 - Find Direction
            
            # region State 22 : Challenge 2 - Laps
            if state == RunStates.CHALLENGE_2_LAPS:
                angle_obstacles, is_green, _, y_center = image_algorithms.find_obstacle_angle_and_draw_lines()
                servo_angle_obstacles = image_algorithms.calculate_servo_angle_from_obstacle(angle_obstacles, is_green)
                servo_angle_walls, _ = image_algorithms.calculate_servo_angle_from_walls()
                angle = image_algorithms.choose_output_angle(servo_angle_walls, servo_angle_obstacles)
                # Accelerate / decelerate if object is far enough
                if y_center is not None:
                    if y_center < OBJECT_FAR_ENOUGH:
                        speed = SPEED_CHALLENGE_2_OBSTACLES
                    else:
                        speed = SPEED_CHALLENGE_2_WALLS
                else:
                    speed = SPEED_CHALLENGE_2_WALLS
                # region Transition to approach state
                if (context_manager.has_completed_laps()):
                    speed = SPEED_CHALLENGE_2_APPROACH
                    state = RunStates.CHALLENGE_2_APPROACH
                    pink_pixel_y = ImageTransformUtils.PIC_HEIGHT - 10
                    pink_pixel_y_backwards = pink_pixel_y
                    if challenge_direction == Direction.LEFT:
                        pink_pixel_x = ImageTransformUtils.PIC_WIDTH - 200
                        pink_pixel_x_backwards = ImageTransformUtils.PIC_WIDTH - 100
                        last_was_green = True
                    else:
                        pink_pixel_x = 200
                        pink_pixel_x_backwards = 100
                        last_was_green = False
                # endregion Transition to approach state
            # endregion State 22 : Challenge 2 - Laps
            
            # region State 23 : Challenge 2 - Approach
            if state == RunStates.CHALLENGE_2_APPROACH:
                angle_obstacles, is_green, obstacle_x, obstacle_y = image_algorithms.find_obstacle_angle_and_draw_lines()
                angle_pink, pink_x, pink_y, side = image_algorithms.find_pink_obstacle_angle()
                # Determine the last obstacle color seen after the 3rd lap
                if obstacle_y is not None:
                    if obstacle_y > OBJECT_CLOSE_ENOUGH:    # Only consider obstacle if it's close
                        last_was_green = is_green
                # Determine whether we follow the pink wall or the obstacle
                if angle_pink is not None and pink_y is not None:
                    if obstacle_y is not None:
                        if (pink_y + 5) > obstacle_y:
                            angle_obstacles = angle_pink
                            is_green = side
                    else:
                        angle_obstacles = angle_pink
                        is_green = side
                servo_angle_obstacles = image_algorithms.calculate_servo_angle_from_obstacle(angle_obstacles, is_green)
                servo_angle_walls, _ = image_algorithms.calculate_servo_angle_from_walls()
                angle = image_algorithms.choose_output_angle(servo_angle_walls, servo_angle_obstacles)
                ImageDrawingUtils.draw_circle(camera_manager.display_image, (pink_pixel_x, pink_pixel_y), 5, (255, 0, 255))
                # Check if we have reached the pink wall
                if pink_x is not None and pink_y is not None:
                    if (challenge_direction == Direction.RIGHT and pink_x < 150 and pink_y > ImageTransformUtils.PIC_HEIGHT - 100) or (challenge_direction == Direction.LEFT and pink_x > ImageTransformUtils.PIC_WIDTH - 150 and pink_y > ImageTransformUtils.PIC_HEIGHT - 100):
                        # Transition to approach state
                        speed = SPEED_CHALLENGE_2_PARKING
                        arduino.send('!', 2000)
                        ok_to_detect_flag = False
                        state = RunStates.CHALLENGE_2_FORWARD
            # endregion State 23 : Challenge 2 - Approach
            
            # region State 24 : Challenge 2 - Forward
            if state == RunStates.CHALLENGE_2_FORWARD:
                angle, _ = image_algorithms.calculate_servo_angle_from_walls(True)
                top_angle = image_algorithms.get_top_line_angle()
                if arduino.read() == 'F':
                    arduino.send('!', 10000000)
                    ok_to_detect_flag = True
                if (ok_to_detect_flag and camera_manager.binary_image[140, ImageTransformUtils.PIC_WIDTH // 2] == 0 and top_angle is not None and parking_direction == Direction.RIGHT) or (ok_to_detect_flag and np.any(camera_manager.cnt_orangeline[ImageTransformUtils.PIC_HEIGHT - 100: ImageTransformUtils.PIC_HEIGHT - 65, ImageTransformUtils.PIC_WIDTH // 2 - 20: ImageTransformUtils.PIC_WIDTH // 2 + 20]) and parking_direction == Direction.LEFT):
                    speed = SPEED_STOP
                    angle = ANGLE_STRAIGHT
                    arduino.send('!', -10000000)
                    start_time = time.time()
                    state = RunStates.CHALLENGE_2_BACKWARDS
            # endregion State 24 : Challenge 2 - Forward
            
            # region State 25 : Challenge 2 - Backwards
            if state == RunStates.CHALLENGE_2_BACKWARDS:
                speed = -SPEED_CHALLENGE_2_ACCELERATED_PARKING
                angle = ANGLE_STRAIGHT
                if time.time() - start_time >= 2.4:
                    speed = -SPEED_CHALLENGE_2_PARKING
                if camera_manager.binary_image[pink_pixel_y_backwards, pink_pixel_x_backwards] == 0:
                    angle = ANGLE_STRAIGHT
                    arduino.send('!', 10000000)
                    state = RunStates.CHALLENGE_2_PARKING
            # endregion State 25 : Challenge 2 - Backwards
            
            # region State 26 : Challenge 2 - Parking
            if state == RunStates.CHALLENGE_2_PARKING:
                speed = SPEED_CHALLENGE_2_ACCELERATED_PARKING
                # Move forward, then enter the parking spot while turning
                if (parking_direction == Direction.LEFT and last_was_green) or (parking_direction == Direction.RIGHT and not last_was_green):
                    # Too close, move forward less, turn less
                    print("Too close to the wall, adjusting parking maneuver")
                    arduino.send('t', ANGLE_STRAIGHT, speed, 1650) # was 1750
                    arduino.send('t', (ANGLE_STRAIGHT + 1) - 37 * parking_direction.value, -speed, 1250)
                else:
                    # Normal
                    print("Normal parking maneuver")
                    arduino.send('t', ANGLE_STRAIGHT, speed, 1800) # was 1850
                    arduino.send('t', (ANGLE_STRAIGHT + 1) - 37 * parking_direction.value, -speed, 1400)
                # Backup straight inside the parking spot
                arduino.send('t', ANGLE_STRAIGHT, -speed, 675)
                # Backup while turning to straighten the robot
                arduino.send('t', (ANGLE_STRAIGHT + 1) + 37 * parking_direction.value, -speed, 1250)
                # Straighten the wheels and stop
                arduino.send('m', ANGLE_STRAIGHT, SPEED_STOP)
                state = RunStates.STOP
                time.sleep(.2)
                with video_thread.lock:
                    camera_manager.capture_image()
                    camera_manager.transform_image()
                parking_quality = image_algorithms.verify_parking_quality()
                print('Out of parking loop')

            # endregion State 26 : Challenge 2 - Parking
            debug_timer.stop()
        
            # region State 9 : Stop
            if state == RunStates.STOP:
                speed = SPEED_STOP
                angle = ANGLE_STRAIGHT
                cv2.destroyAllWindows()
                state = RunStates.INITIALIZATIONS
            # endregion State 9 : Stop

            # region To-do end of every loop
            if state is not RunStates.INITIALIZATIONS and state is not RunStates.WAIT_FOR_START:
                arduino.send('m', angle, speed)
                context_manager.set_state(state)
                
            time.sleep(0.001)
            key = cv2.waitKey(1) # Let OpenCV update the window
            if key == 27: # Exit on ESC
                if (speed != 0) and context_manager.get_challenge() == 1:
                    speed = SPEED_STOP
                else:
                    break
            # endregion To-do end of every loop
            
    finally:
        if 'video_thread' in locals():
            video_thread.stop()
            video_thread.join()
        arduino.send('m', ANGLE_STRAIGHT, SPEED_STOP)
        cv2.destroyAllWindows()