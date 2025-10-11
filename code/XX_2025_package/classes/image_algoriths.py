from utils.image_transform_utils import ImageTransformUtils
from utils.image_color_utils import ImageColorUtils
import numpy as np
import math
from utils.enums import Direction
from utils.image_drawing_utils import ImageDrawingUtils
from utils.enums import StartPosition
from collections import namedtuple
 
MIDDLE_X = 320
LEFT_OBSTACLE_X_THRESHOLD = 40
RIGHT_OBSTACLE_X_THRESHOLD = ImageTransformUtils.PIC_WIDTH - LEFT_OBSTACLE_X_THRESHOLD
MIN_ANGLE = 48
MAX_ANGLE = 128
STRAIGHT_ANGLE = 86
OBJECT_LINE_ANGLE_THRESHOLD = 45
NBR_COLS = 10

ChallengeParameters = namedtuple('ChallengeParameters', ['kp', 'kd', 'base_threshold', 'offsets'])
# Challenge configs for wall follower
CHALLENGE_CONFIG = {
    1: ChallengeParameters(kp = 0.18, kd = 0.25 , base_threshold = ImageTransformUtils.PIC_HEIGHT, offsets = [-100, -30, 40]),
    2: ChallengeParameters(kp = 0.35, kd = 0.25 , base_threshold = ImageTransformUtils.PIC_HEIGHT, offsets = [-140, -100   ]),
    3: ChallengeParameters(kp = 1.5 , kd = 1.0  , base_threshold = ImageTransformUtils.PIC_HEIGHT, offsets = [-30          ]),
    4: ChallengeParameters(kp = 0.35, kd = 0.25 , base_threshold = ImageTransformUtils.PIC_HEIGHT, offsets = [-100         ])
}

class ImageAlgorithms:
    START_WALL_HEIGHT_THRESHOLD = 34
    BACK_ZONE_WALL_HEIGHT = 30
    FRONT_ZONE_WALL_HEIGHT = 40

    def __init__(self, context_manager, camera_manager):
        self.context_manager = context_manager
        self.camera_manager = camera_manager
        self.old_p_adjust = 0
        self.old_angle = 0
        self.old_is_green = 0
        self.last_color = None
        self.inner_wall_warning = False

    def get_direction_from_lines(self):
        """
        Determine the direction by looking at which of the blue or orange lines is longer (Challenge 1)
        I/O:
            camera_object: CameraObject containing the binary image with blue and orange lines
        Effects:
            Sets the direction in context_manager
        """
        print(self.camera_manager.length_blue)
        print(self.camera_manager.length_orange)
        direction = Direction.LEFT if self.camera_manager.length_blue > self.camera_manager.length_orange else Direction.RIGHT
        self.context_manager.set_direction(direction)

    def get_direction_from_parking(self, camera_object):
        """
        Determine the direction by looking at which half of the image has more white pixels (Challenge 2)
        I/O: 
            camera_object: CameraObject containing the polygon image
        Effects:
            Sets the direction in context_manager
        """
        left_side_white_pixels = np.sum(camera_object.polygon_image[:, :ImageTransformUtils.PIC_WIDTH // 2] == 255)
        right_side_white_pixels = np.sum(camera_object.polygon_image[:, ImageTransformUtils.PIC_WIDTH // 2:] == 255)
        self.context_manager.set_direction(Direction.LEFT if left_side_white_pixels > right_side_white_pixels else Direction.RIGHT)

    @staticmethod
    def find_black_from_bottom(img, col_range):
        """
        Find the first black pixel in each column starting from the bottom of the image
        I/O:
            img: binary image
            col_range: range of columns to check
            return: list of y-values where the first black pixel was found in each column of col_range
        """
        y_vals = []
        for x in col_range:
            for y in reversed(range(ImageTransformUtils.PIC_HEIGHT - 20)):
                # Start x pixels from the bottom so it skips inconsistencies in the polygon's bottom row
                if img[y,x] == 0:
                    y_vals.append(y)
                    break
            else:
                y_vals.append(0)
        return y_vals

    @staticmethod
    def find_black_sides(img, rotation, row_range):
        """
        Find the first black pixel in each row starting from the middle column of the image
        I/O:
            img: binary image
            rotation: Direction enum, either LEFT or RIGHT
            row_range: range of rows to check
            return: list of x-values where the first black pixel was found in each row of row_range
        """
        end_index = 0 if rotation.value == -1 else ImageTransformUtils.PIC_WIDTH - 1
        x_vals = []
        for y in row_range:
            for x in range(ImageTransformUtils.PIC_WIDTH // 2, end_index, rotation.value):
                # Start a middle column, and go left or right depending on the rotation
                if img[y,x] == 0:       
                    x_vals.append(x)
                    break
            else:
                x_vals.append(end_index)
        return x_vals
    
    @staticmethod
    def get_offset_from_lap(challenge, lap_count, quarter_lap_count):
        """
        Get the offset value based on the challenge, lap count, and quarter lap count
        I/O:
            challenge: current challenge number
            lap_count: current lap count
            quarter_lap_count: current quarter lap count
            return: offset value for the given challenge and lap counts
        """
        config = CHALLENGE_CONFIG[challenge]
        offset = config.offsets

        if challenge == 1:
            if lap_count == 0:
                if quarter_lap_count == 0:  
                    return offset[0]            # Challenge 1 first quarter offset
                elif quarter_lap_count == 1:
                    return offset[1]            # Challenge 1 second quarter offset
                else:
                    return offset[2]            # Challenge 1 normal offset
            else:
                return offset[2]                # Challenge 1 normal offset
        elif challenge == 2:
            if lap_count == 0:
                if quarter_lap_count == 0:
                    return offset[0]
                else:
                    return offset[1]
            else:
                return offset[1]
        else:
            return offset[0]                    # Always use the only offset

    def calculate_wall_threshold_kp_kd(self, challenge_demanded = None):
        """
        Calculate the threshold, kp, and kd values based on the challenge and lap count
        I/O:
            return: tuple of (threshold, kp, kd)
        """
        if challenge_demanded is not None:
            challenge = challenge_demanded
        else:
            challenge = self.context_manager.CHALLENGE
        lap = self.context_manager.get_lap_count()
        quarter_lap = self.context_manager.get_quarter_lap_count()
        config = CHALLENGE_CONFIG[challenge]
        base_threshold = config.base_threshold
        offset = self.get_offset_from_lap(challenge, lap, quarter_lap)
        threshold = base_threshold + offset
        kp = config.kp
        kd = config.kd
        return threshold, kp, kd

    def find_wall_to_follow(self, inverted = False):
        """
        Find the wall to follow based on the black pixels in the image
        I/O:
            img: binary image (polygon image)
            NBR_COLS: number of columns to consider for the calculation (default is 10)
            return: position of neareast wall with y_vals and x_vals
        """
        direction = self.context_manager.get_direction()
        if inverted:
            if direction == Direction.LEFT: 
                direction = Direction.RIGHT
            else: 
                direction = Direction.LEFT
        if direction == Direction.LEFT:
            cols = range(0, NBR_COLS)
        else:
            cols = range(ImageTransformUtils.PIC_WIDTH - NBR_COLS, ImageTransformUtils.PIC_WIDTH)
        rows = range(ImageTransformUtils.PIC_HEIGHT - 3*NBR_COLS, ImageTransformUtils.PIC_HEIGHT - 2*NBR_COLS)
        y_vals = ImageAlgorithms.find_black_from_bottom(self.camera_manager.polygon_image, cols)
        x_vals = ImageAlgorithms.find_black_sides(self.camera_manager.polygon_image, direction, rows)
        avg_y = np.mean(y_vals)
        avg_x = np.mean(x_vals)
        # Adjust if follows right wall
        if direction == Direction.RIGHT : avg_x = 640 - avg_x
        if avg_y >= 259.0 : avg_y = ImageTransformUtils.PIC_HEIGHT
        return avg_x, avg_y

    def calculate_servo_angle_from_walls(self, challenge_3 = False):
        """
        Calculate the servo's angle
        I/O:
            img: binary image (polygon image)
            return: servo angle to follow the wall
        """
        is_corner = False
        direction = self.context_manager.get_direction()
        # Get position of nearest wall from find_wall_to_follow()
        avg_x, avg_y = self.find_wall_to_follow()
        # Get threshold, kp and kd values based on the challenge
        if challenge_3:
            threshold, kp, kd = self.calculate_wall_threshold_kp_kd(3)
        else:
            threshold, kp, kd = self.calculate_wall_threshold_kp_kd()
        # If speed is 3000, do not reduce the kp to 0.1
        # If speed is 4000, reduce the kp to 0.1
        if self.inner_wall_warning:
            kp = 0.1
            kd = 0
        threshold_y = min(threshold, ImageTransformUtils.PIC_HEIGHT)
        if direction == Direction.LEFT:
            threshold_x = threshold - threshold_y
            new_avg_x = avg_x
        else:
            threshold_x = 640 - (threshold - threshold_y)
            new_avg_x = 640 - avg_x
        # Draw polygon on display image
        ImageDrawingUtils.draw_contour(self.camera_manager.display_image, self.camera_manager.polygon_lines, (0, 0, 255))
        # Draw circle for threshold of wall following
        ImageDrawingUtils.draw_circle(self.camera_manager.display_image, (threshold_x, threshold_y), 10, (255, 0, 0))
        # Draw circle for current position of the wall
        ImageDrawingUtils.draw_circle(self.camera_manager.display_image, (int(new_avg_x), int(avg_y)), 7, (0, 255, 255))
        # Get proportional adjustment
        p_adjust = avg_y + avg_x - threshold
        # Get current - previous diff
        p_compare = p_adjust - self.old_p_adjust
        if p_compare < (-1 * (ImageTransformUtils.PIC_HEIGHT // 2.5)):
            print("p_compare is : ", p_compare)
            is_corner = True
        # Get differential adjustment
        d_adjust = (p_compare) * kd
        # Get output angle
        angle =  STRAIGHT_ANGLE + direction.value * (int((p_adjust) * kp) + d_adjust)
        # Save p_adjust for the next iteration
        self.old_p_adjust = p_adjust
        # Limit angle to min and max values
        if angle < MIN_ANGLE:
            angle = MIN_ANGLE
        elif angle > MAX_ANGLE:
            angle = MAX_ANGLE
        return int(angle), is_corner
    
    def check_last_corner_position(self):
        """
        Check whether the last corner is close or far from the middle
        I/O:
            return: 'C' if close to the corner, 'F' if far from the corner
        """
        # Get the average y position of the outer wall
        _, avg_y = self.find_wall_to_follow(True)
        if avg_y > ImageTransformUtils.PIC_HEIGHT // 2:
            return 'C'  # Close
        else:
            return 'F'  # Far

    def check_inner_wall_crash(self, object_height):
        """
        Determines if the robot is too close to the inner wall while detecting an obstacle in a further section
        I/O:
            object_height: height of the detected object's center
            return: True if the robot is too close to the inner wall, False otherwise
        """
        # Make sure there's an object, otherwise return True (to follow walls)
        if object_height is None:
            return True
        # Set 3 detection points
        if self.context_manager.get_direction() == Direction.RIGHT:
            detection_points = [
                (ImageTransformUtils.PIC_HEIGHT - 130, ImageTransformUtils.PIC_WIDTH - 200),
                (ImageTransformUtils.PIC_HEIGHT - 100, ImageTransformUtils.PIC_WIDTH - 175),
                (ImageTransformUtils.PIC_HEIGHT - 70, ImageTransformUtils.PIC_WIDTH - 150)
            ]
        else:
            detection_points = [
                (ImageTransformUtils.PIC_HEIGHT - 130, 200),
                (ImageTransformUtils.PIC_HEIGHT - 100, 175),
                (ImageTransformUtils.PIC_HEIGHT - 70, 150 )
            ]
        # Check if any detection point is on the wall, if so, return True
        for y, x in detection_points:
            ImageDrawingUtils.draw_circle(self.camera_manager.display_image, (x, y), 3, (255, 0, 0))
            if self.camera_manager.polygon_image[y, x] == 0 and object_height < ImageTransformUtils.PIC_HEIGHT - 170:
                self.inner_wall_warning = True
                return True
        return False
    
    def check_outer_wall_crash(self):
        """
        Determines if the robot is too close to the outer wall
        I/O:
            return: True if the robot is too close to the outer wall
        """
        # Get the crash detection point
        crash_detect_x = ImageTransformUtils.PIC_WIDTH // 2
        crash_detect_y = ImageTransformUtils.PIC_HEIGHT - 150
        # Draw the point at which we check if outer wall is too close
        ImageDrawingUtils.draw_circle(self.camera_manager.display_image, (crash_detect_x, crash_detect_y), 3, (255, 0, 0))
        # Return True if the outer wall is detected
        return (self.camera_manager.polygon_image[crash_detect_y, crash_detect_x] == 0)

    def find_obstacle_angle_and_draw_lines(self):
        """
        Find the obstacle, draw a line between its center and a reference, return the line's angle
        I/O:
            target_img: colored image in which we draw
            return: line's angle, whether the object is green or not, the obstacle's x_center, the obstacle's y_center
        """
        # Deactivate inner wall warning
        self.inner_wall_warning = False
        # Check if the outer wall in front is too close
        if self.check_outer_wall_crash():
            if self.context_manager.get_direction() == Direction.RIGHT:
                return 1000, None, None, None
            else:
                return -1000, None, None, None
        # Get the biggest rectangle from find_rect() - in the future, we could use the 4th output to use the second biggest obstacle
        _, _, rect, rect2 = ImageDrawingUtils.find_rect(self.camera_manager.obstacle_image, self.camera_manager.polygon_image)
        # Check if a rectangle was found
        if rect is None:
            return None, None, None, None
        
        
        #########################################
        # Verify if a second rectangle is closer than the first one
        if rect2 is not None:
            y_center2 = rect2[0][1]
            if y_center2 > rect[0][1]:
                rect = rect2
        #########################################

        # Get the center of the rectangle
        x_center = rect[0][0]
        y_center = rect[0][1]
        # Check if the object is too low
        if y_center > ImageTransformUtils.PIC_HEIGHT - 60:
            if y_center > ImageTransformUtils.PIC_HEIGHT - 30:
                # Object is too low, ignore it
                return None, None, None, None
            else:
                # Object is quite close, use previous adjustment
                return self.old_angle, self.old_is_green, x_center, y_center
        # Check if the object is too high
        #if y_center < ImageTransformUtils.PIC_HEIGHT - 340:# was 240
            # Object is too high, ignore it
        #    return None, None, None, None
        # Check if the inner wall is too close
        if self.check_inner_wall_crash(y_center):
            return None, None, None, None
        # Check if the obstacle is green or red
        is_green = ImageColorUtils.is_rect_green(self.camera_manager.hsv_image, rect)
        # Create and draw a line from the center of the object to the left or right side of the image
        # Line needs to be at x degrees (the angle threshold) to be able to pass around the obstacle
        if is_green:
            if self.context_manager.has_completed_laps():
                self.last_color = 1
            ImageDrawingUtils.draw_line(self.camera_manager.display_image, (x_center, y_center), (RIGHT_OBSTACLE_X_THRESHOLD, ImageTransformUtils.PIC_HEIGHT))
            rad_angle = math.atan2(y_center - ImageTransformUtils.PIC_HEIGHT, x_center - RIGHT_OBSTACLE_X_THRESHOLD)
        else:
            if self.context_manager.has_completed_laps():
                self.last_color = 0
            ImageDrawingUtils.draw_line(self.camera_manager.display_image, (x_center, y_center), (LEFT_OBSTACLE_X_THRESHOLD, ImageTransformUtils.PIC_HEIGHT))
            rad_angle = math.atan2(y_center - ImageTransformUtils.PIC_HEIGHT, x_center - LEFT_OBSTACLE_X_THRESHOLD)
        # Calculate the angle in degrees
        angle = 90 + math.degrees(rad_angle)
        self.old_angle = angle
        self.old_is_green = is_green
        return angle, is_green, x_center, y_center
    

    def find_pink_obstacle_angle(self):
        """
        Detect the largest pink obstacle and calculate the avoidance angle.

        This method finds the largest pink obstacle in the image, optionally considers a second obstacle
        if it is more relevant based on the robot's direction, and computes the angle needed to steer
        around it. The angle is calculated by drawing a line from the obstacle's center to the appropriate
        side of the image, depending on the current wall-following direction.

        Returns:
            tuple: (angle, x_center, y_center, left)
                - angle (float): The calculated avoidance angle in degrees, or None if no valid obstacle is found.
                - x_center (int): The x-coordinate of the obstacle's center.
                - y_center (int): The y-coordinate of the obstacle's center.
                - left (bool): True if the robot should pass the obstacle on the left, False otherwise.
        """
        direction = self.context_manager.get_direction()
        _, _, rect, rect2 = ImageDrawingUtils.find_rect(self.camera_manager.pink_mask, self.camera_manager.polygon_image)
        # Check if a rectangle was found
        if rect is None:
            return None, None, None, None
        # Get the center of the rectangle
        x_center = rect[0][0]
        y_center = rect[0][1]
        if rect2 is not None:
            # Get the center of the second rectangle
            x_center2 = rect2[0][0]
            y_center2 = rect2[0][1]
            if (x_center2 > x_center and direction == Direction.RIGHT) or (x_center2 < x_center and direction == Direction.LEFT):
                # print("Following the second wall")
                x_center = x_center2
                y_center = y_center2
        # Check if the object is too low
        if y_center > ImageTransformUtils.PIC_HEIGHT - 30:
            return None, None, None, None
        # Check if the object is too high
        if y_center < ImageTransformUtils.PIC_HEIGHT - 230:# was 60
            # Object is too high, ignore it
            return None, None, None, None

        # Create and draw a line from the center of the object to the left or right side of the image
        # Line needs to be at x degrees (the angle threshold) to be able to pass around the obstacle
        if direction == Direction.LEFT:
            left = True
            ImageDrawingUtils.draw_line(self.camera_manager.display_image, (x_center, y_center), (ImageTransformUtils.PIC_WIDTH, ImageTransformUtils.PIC_HEIGHT))
            rad_angle = math.atan2(y_center - (ImageTransformUtils.PIC_HEIGHT), x_center - (ImageTransformUtils.PIC_WIDTH - 20))
        else:
            left = False
            ImageDrawingUtils.draw_line(self.camera_manager.display_image, (x_center, y_center), (0, ImageTransformUtils.PIC_HEIGHT))
            rad_angle = math.atan2(y_center - (ImageTransformUtils.PIC_HEIGHT), x_center - 20)
        # Calculate the angle in degrees
        angle = 90 + math.degrees(rad_angle)
        return angle, x_center, y_center, left

    @staticmethod
    def calculate_servo_angle_from_obstacle(object_angle, is_green):
        """
        Calculate the servo angle based on the obstacle's angle and color
        I/O:
            object_angle: angle of the line from the obstacle to the reference point
            is_green: boolean indicating if the obstacle is green (True) or red (False)
            return: servo angle to avoid the obstacle
        """
        if object_angle is None:
            return None
        kp = 1.5
        if is_green:
            servo_angle = STRAIGHT_ANGLE - ((object_angle + OBJECT_LINE_ANGLE_THRESHOLD) * kp) # green obstacle
        else:
            servo_angle = STRAIGHT_ANGLE - ((object_angle - OBJECT_LINE_ANGLE_THRESHOLD) * kp) # red obstacle
        if servo_angle < MIN_ANGLE:
            servo_angle = MIN_ANGLE
        elif servo_angle > MAX_ANGLE:
            servo_angle = MAX_ANGLE
        return int(servo_angle)

    @staticmethod
    def choose_output_angle(angle_walls, angle_obstacles):
        if angle_obstacles is None:
            return angle_walls
        return angle_obstacles

    def get_top_line_angle(self):
        """
        Calculate the angle of the top (back) wall line segment that crosses the middle of the image.

        This method iterates through the polygon lines detected in the image, finds the line segment that crosses
        the horizontal middle (with a direction-dependent offset), and returns its angle in degrees.

        Returns:
            float or None: The angle in degrees of the top line crossing the middle, or None if not found.
        """
        is_in_middle = False
        poly_lines = self.camera_manager.polygon_lines
        
        # finding the back wall line
        for i in range(len(poly_lines)):
            pt1 = poly_lines[i][0]
            pt2 = poly_lines[(i+1) % len(poly_lines)][0]
            dx = pt2[0] - pt1[0]
            dy = pt2[1] - pt1[1]
            if (pt2[0] < (ImageTransformUtils.PIC_WIDTH // 2 + self.context_manager.get_direction().value * 50) < pt1[0] 
                or pt1[0] < (ImageTransformUtils.PIC_WIDTH // 2 + self.context_manager.get_direction().value * 50) < pt2[0]):
                is_in_middle = True
            angle = np.degrees(np.arctan2(dy,dx))
            
            # different cut-off depending on the challenge
            if self.context_manager.CHALLENGE == 1:
                if ((angle > 170) or (angle < -170)) and is_in_middle:
                    return angle
            else:
                if ((angle > 178) or (angle < -178)) and is_in_middle:
                    return angle
        return None

    
    def get_starting_position(self):
        """
        Determine the starting position (front or back) by measuring the distance to the back wall.
        I/O:
            return: StartPosition enum indicating FRONT or BACK
        """
        distance = self.get_back_wall_distance()
        self.context_manager.set_parking_distance(distance)

        
        if distance < ImageAlgorithms.START_WALL_HEIGHT_THRESHOLD:
            return StartPosition.BACK
        else:
            return StartPosition.FRONT
        
        
    def get_back_wall_distance(self):
        """
        Estimate the distance to the back wall by averaging the y-values of black pixels in the middle columns.
        I/O:
            return: estimated distance to the back wall
        """
        NBR_COLS = 10
        mid_x = ImageTransformUtils.PIC_WIDTH // 2
        start = mid_x - (NBR_COLS // 2)
        end = start + NBR_COLS
        cols = range(start, end)
        
        return np.mean(self.find_black_from_bottom(self.camera_manager.polygon_image, cols))