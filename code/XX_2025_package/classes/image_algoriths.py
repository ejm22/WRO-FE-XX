from XX_2025_package.utils.image_transform_utils import ImageTransformUtils
from XX_2025_package.utils.image_color_utils import ImageColorUtils
import numpy as np
import math
from XX_2025_package.utils.enums import Direction
from XX_2025_package.utils.image_drawing_utils import ImageDrawingUtils
from XX_2025_package.utils.enums import StartPosition
from collections import namedtuple
 
MIDDLE_X = 320
LEFT_OBSTACLE_X_THRESHOLD = 40
RIGHT_OBSTACLE_X_THRESHOLD = ImageTransformUtils.PIC_WIDTH - LEFT_OBSTACLE_X_THRESHOLD
MIN_ANGLE = 48
MAX_ANGLE = 128
STRAIGHT_ANGLE = 85
OBJECT_LINE_ANGLE_THRESHOLD = 45

ChallengeParameters = namedtuple('ChallengeParameters', ['kp', 'kd', 'base_threshold', 'offsets'])
CHALLENGE_CONFIG = {
    1: ChallengeParameters(kp = 0.2, kd = 0.25 , base_threshold = ImageTransformUtils.PIC_HEIGHT, offsets = [-100, -30, 40  ]),
    2: ChallengeParameters(kp = 0.35, kd = 0.25 , base_threshold = ImageTransformUtils.PIC_HEIGHT, offsets = [-100           ]),
    3: ChallengeParameters(kp = 1.5 , kd = 1    , base_threshold = ImageTransformUtils.PIC_HEIGHT, offsets = [-40            ]),
    4: ChallengeParameters(kp = 0.35, kd = 0.25 , base_threshold = ImageTransformUtils.PIC_HEIGHT, offsets = [-100           ])
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
            for y in reversed(range(ImageTransformUtils.PIC_HEIGHT - 30)):
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

    def find_wall_to_follow(self, img, nbr_cols = 10):
        """
        Find the wall to follow based on the black pixels in the image
        I/O:
            img: binary image (polygon image)
            nbr_cols: number of columns to consider for the calculation (default is 10)
            return: position of neareast wall with y_vals and x_vals
        """
        direction = self.context_manager.get_direction()
        if direction == Direction.LEFT:
            cols = range(0, nbr_cols)
        else:
            cols = range(ImageTransformUtils.PIC_WIDTH - nbr_cols, ImageTransformUtils.PIC_WIDTH)
        rows = range(ImageTransformUtils.PIC_HEIGHT - 3*nbr_cols, ImageTransformUtils.PIC_HEIGHT - 2*nbr_cols)
        y_vals = ImageAlgorithms.find_black_from_bottom(img, cols)
        x_vals = ImageAlgorithms.find_black_sides(img, direction, rows)
        avg_y = np.mean(y_vals)
        avg_x = np.mean(x_vals)
        # Adjust if follows right wall
        if direction == Direction.RIGHT : avg_x = 640 - avg_x
        return avg_x, avg_y

    def calculate_servo_angle_from_walls(self, img, challenge_3 = False):
        """
        Calculate the servo's angle
        I/O:
            img: binary image (polygon image)
            return: servo angle to follow the wall
        """
        direction = self.context_manager.get_direction()
        # Get position of nearest wall from find_wall_to_follow()
        avg_x, avg_y = self.find_wall_to_follow(img)
        # Get threshold, kp and kd values based on the challenge
        if challenge_3:
            threshold, kp, kd = self.calculate_wall_threshold_kp_kd(3)
        else:
            threshold, kp, kd = self.calculate_wall_threshold_kp_kd()
        threshold_y = min(threshold, ImageTransformUtils.PIC_HEIGHT)
        if direction == Direction.LEFT:
            threshold_x = max(0, threshold - threshold_y)
        else:
            threshold_x = 640 - max(0, threshold - threshold_y)
        ImageDrawingUtils.draw_contour(self.camera_manager.display_image, self.camera_manager.polygon_lines, (0, 0, 255))
        ImageDrawingUtils.draw_circle(self.camera_manager.display_image, (threshold_x, threshold_y), 3, (255, 255, 0))
        ImageDrawingUtils.draw_circle(self.camera_manager.display_image, (avg_x, avg_y), 3, (0, 255, 0))
        # Get proportional adjustment
        p_adjust = avg_y + avg_x - threshold
        # Get differential adjustment
        d_adjust = (p_adjust - self.old_p_adjust) * kd
        # Get output angle
        angle =  STRAIGHT_ANGLE + direction.value * (int((p_adjust) * kp) + d_adjust)
        # Save p_adjust for the next iteration
        self.old_p_adjust = p_adjust
        # Limit angle to min and max values
        if angle < MIN_ANGLE:
            angle = MIN_ANGLE
        elif angle > MAX_ANGLE:
            angle = MAX_ANGLE
        return int(angle)
    
    def check_inner_wall_crash(self, object_height):
        """
        Determines if the robot is too close to the inner wall while detecting an obstacle in a further section
        I/O:
            object_height: height of the detected object's center
            return: True if the robot is too close to the inner wall, False otherwise
        """
        if object_height is None:
            return True
        if self.context_manager.get_direction() == Direction.RIGHT:
            return (object_height < ImageTransformUtils.PIC_HEIGHT - 170) and (self.camera_manager.polygon_image[ImageTransformUtils.PIC_HEIGHT - 130, ImageTransformUtils.PIC_WIDTH - 200] == 0)
        else:
            return (object_height < ImageTransformUtils.PIC_HEIGHT - 170) and (self.camera_manager.polygon_image[ImageTransformUtils.PIC_HEIGHT - 130, 200] == 0)

    def find_obstacle_angle_and_draw_lines(self, target_img):
        """
        Find the obstacle, draw a line between its center and a reference, return the line's angle
        I/O:
            target_img: colored image in which we draw
            return: line's angle, target_img, and whether the object is green or not
        """

        # Zero the last 30 rows
        #self.camera_manager.obstacle_image[-30:, :] = 0
    
        _, _, rect = ImageDrawingUtils.find_rect(self.camera_manager.obstacle_image, self.camera_manager.polygon_image)
        # Check if a rectangle was found
        if rect is None:
            return None, target_img, None, None, None
        # Get the center of the rectangle
        x_center = rect[0][0]
        y_center = rect[0][1]
        # Check if the object is too low
        if y_center > ImageTransformUtils.PIC_HEIGHT - 60:
            if y_center > ImageTransformUtils.PIC_HEIGHT - 30:
                # Object is too low, ignore it
                return None, target_img, None, None, None
            else:
                # Object is quite close, use previous adjustment
                return self.old_angle, None, self.old_is_green, x_center, y_center
        # Check if the object is too high
        if y_center < ImageTransformUtils.PIC_HEIGHT - 240:# was 60
            # Object is too high, ignore it
            return None, target_img, None, None, None
        
        # Draw the point at which we check if the inner wall is too close
        if self.context_manager.get_direction() == Direction.RIGHT:
            ImageDrawingUtils.draw_circle(target_img, (ImageTransformUtils.PIC_WIDTH - 200, ImageTransformUtils.PIC_HEIGHT - 130), 3, (255, 0, 0))
        else:
            ImageDrawingUtils.draw_circle(target_img, (200, ImageTransformUtils.PIC_HEIGHT - 130), 3, (255, 0, 0))
        # Check if the inner wall is too close
        if self.check_inner_wall_crash(y_center):
            return None, target_img, None, None, None

        # Check if the obstacle is green or red
        is_green = ImageColorUtils.is_rect_green(self.camera_manager.hsv_image, rect)
        # Create and draw a line from the center of the object to the left or right side of the image
        # Line needs to be at x degrees (the angle threshold) to be able to pass around the obstacle
        if is_green:
            ImageDrawingUtils.draw_line(target_img, (x_center, y_center), (RIGHT_OBSTACLE_X_THRESHOLD, ImageTransformUtils.PIC_HEIGHT))
            rad_angle = math.atan2(y_center - ImageTransformUtils.PIC_HEIGHT, x_center - RIGHT_OBSTACLE_X_THRESHOLD)
        else:
            ImageDrawingUtils.draw_line(target_img, (x_center, y_center), (LEFT_OBSTACLE_X_THRESHOLD, ImageTransformUtils.PIC_HEIGHT))
            rad_angle = math.atan2(y_center - ImageTransformUtils.PIC_HEIGHT, x_center - LEFT_OBSTACLE_X_THRESHOLD)
        # Calculate the angle in degrees
        angle = 90 + math.degrees(rad_angle)
        self.old_angle = angle
        self.old_is_green = is_green
        return angle, target_img, is_green, x_center, y_center

    def find_pink_obstacle_angle(self, target_img):
        direction = self.context_manager.get_direction()
        _, _, rect = ImageDrawingUtils.find_rect(self.camera_manager.pink_mask, self.camera_manager.polygon_image)
        # Check if a rectangle was found
        if rect is None:
            return None, target_img, None, None, None
        # Get the center of the rectangle
        x_center = rect[0][0]
        y_center = rect[0][1]
        # Check if the object is too low
        if y_center > ImageTransformUtils.PIC_HEIGHT - 30:
            return None, target_img, None, None, None
        # Check if the object is too high
        if y_center < ImageTransformUtils.PIC_HEIGHT - 230:# was 60
            # Object is too high, ignore it
            return None, target_img, None, None, None

        # Create and draw a line from the center of the object to the left or right side of the image
        # Line needs to be at x degrees (the angle threshold) to be able to pass around the obstacle
        if direction == Direction.LEFT:
            left = True
            ImageDrawingUtils.draw_line(target_img, (x_center, y_center), (ImageTransformUtils.PIC_WIDTH, ImageTransformUtils.PIC_HEIGHT))
            rad_angle = math.atan2(y_center - ImageTransformUtils.PIC_HEIGHT, x_center - ImageTransformUtils.PIC_WIDTH)
        else:
            left = False
            ImageDrawingUtils.draw_line(target_img, (x_center, y_center), (0, ImageTransformUtils.PIC_HEIGHT))
            rad_angle = math.atan2(y_center - ImageTransformUtils.PIC_HEIGHT, x_center - 0)
        # Calculate the angle in degrees
        angle = 90 + math.degrees(rad_angle)
        return angle, target_img, x_center, y_center, left

    @staticmethod
    def calculate_servo_angle_from_obstacle(object_angle, is_green, pink = 0):
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
            #print("Walls at angle : ", angle_walls)
            return angle_walls
        #print("Obstacles at angle : ", angle_obstacles)
        return angle_obstacles

    def get_top_line_angle(self, use_cutoff):
        poly_lines = self.camera_manager.polygon_lines
        for i in range(len(poly_lines)):
            pt1 = poly_lines[i][0]
            pt2 = poly_lines[(i+1) % len(poly_lines)][0]
            dx = pt2[0] - pt1[0]
            dy = pt2[1] - pt1[1]
            angle = np.degrees(np.arctan2(dy,dx))
            if use_cutoff is False or ((angle > 178) or (angle < -178)):
                #print("Top wall angle = ", angle)
                return angle
        return None

    @staticmethod
    def calculate_servo_angle_parking(wall_angle):
        if wall_angle  is None:
            return None
        #servo_angle = math.pow(object_angle * 0.1, 2) * 0.5
        if wall_angle > 0:
            servo_angle = STRAIGHT_ANGLE - (wall_angle -180) * 10
        else:
            servo_angle = STRAIGHT_ANGLE - (wall_angle +180) * 10

        if servo_angle < MIN_ANGLE:
            servo_angle = MIN_ANGLE
        elif servo_angle > MAX_ANGLE:
            servo_angle = MAX_ANGLE
        return int(servo_angle)
    
    def get_starting_position(self):
        distance = self.get_back_wall_distance()
        highest_y = self.get_top_line_distance()
        self.context_manager.set_parking_distance(highest_y)

        
        if distance < ImageAlgorithms.START_WALL_HEIGHT_THRESHOLD:
            return StartPosition.BACK
        else:
            return StartPosition.FRONT
        
        
    def get_back_wall_distance(self):
        nbr_cols = 10
        mid_x = ImageTransformUtils.PIC_WIDTH // 2
        start = mid_x - (nbr_cols // 2)
        end = start + nbr_cols
        cols = range(start, end)
        
        return np.mean(self.find_black_from_bottom(self.camera_manager.polygon_image, cols))

    
    def get_top_line_distance(self):
        if self.camera_manager.polygon_lines is None:
            return None
        
        poly_lines = self.camera_manager.polygon_lines
        
        # start value of infinity
        highest_y = float('inf')
        
        for i in range(len(poly_lines)):
            pt1 = poly_lines[i][0]
            pt2 = poly_lines[(i+1) % len(poly_lines)][0]
            
            line_y = min(pt1[1], pt2[1])
            
            if line_y < highest_y:
                highest_y = line_y

        print(highest_y)
        
        return highest_y
