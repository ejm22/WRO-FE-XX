from XX_2025_package.utils.image_transform_utils import ImageTransformUtils
from XX_2025_package.utils.image_color_utils import ImageColorUtils
import numpy as np
import math
from XX_2025_package.utils.enums import Direction
from XX_2025_package.utils.image_drawing_utils import ImageDrawingUtils
from XX_2025_package.utils.enums import StartPostition

MIDDLE_X = 320
START_WALL_HEIGHT_THRESHOLD = ImageTransformUtils.PIC_HEIGHT - 115
LEFT_OBSTACLE_X_THRESHOLD = 40
RIGHT_OBSTACLE_X_THRESHOLD = ImageTransformUtils.PIC_WIDTH - LEFT_OBSTACLE_X_THRESHOLD
old_diff = 0
old_angle = 0
old_is_green = 0
direction = Direction.LEFT
#threshold = 400

class ImageAlgorithms:
    #direction = Direction.RIGHT

    @classmethod
    def get_direction_from_parking(cls, camera_object):
        left = np.sum(camera_object.binary_image[:, :ImageTransformUtils.PIC_WIDTH // 2])
        right = np.sum(camera_object.binary_image[:, ImageTransformUtils.PIC_WIDTH // 2:])
        cls.direction = Direction.LEFT if left > right else Direction.RIGHT
        return cls.direction

    @classmethod
    def get_direction_from_lines(cls, camera_object):
        print("Lol")
        cls.direction = Direction.LEFT if camera_object.length_blue > camera_object.length_orange else Direction.RIGHT
        return cls.direction

    @classmethod
    def get_threshold(cls, elapsed):
        #cls.threshold = 250 if elapsed < 2.25 else 400
        cls.threshold = 400

    @staticmethod
    def find_black_from_bottom(img, col_range):
        y_vals = []
        for x in col_range:
            for y in reversed(range(ImageTransformUtils.PIC_HEIGHT - 30)):
                if img[y,x] == 0:
                    y_vals.append(y)
                    break
            else:
                y_vals.append(0)
        return y_vals

    @staticmethod
    def find_black_sides(img, rotation, row_range):
        end_index = 0 if rotation.value == -1 else ImageTransformUtils.PIC_WIDTH - 1
        x_vals = []
        for y in row_range:
            for x in range(ImageTransformUtils.PIC_WIDTH // 2, end_index, rotation.value):
                if img[y,x] == 0:       
                    x_vals.append(x)
                    break
            else:
                x_vals.append(end_index)
        return x_vals
    
    @staticmethod
    def find_angle_from_img(img, nbr_cols = 10):
        global old_diff
        direction = ImageAlgorithms.direction
        cols = range(0, nbr_cols) if direction == Direction.LEFT else range(ImageTransformUtils.PIC_WIDTH - nbr_cols, ImageTransformUtils.PIC_WIDTH)
        rows = range(ImageTransformUtils.PIC_HEIGHT - 3*nbr_cols, ImageTransformUtils.PIC_HEIGHT - 2*nbr_cols)

        y_vals = ImageAlgorithms.find_black_from_bottom(img, cols)
        x_vals = ImageAlgorithms.find_black_sides(img, direction, rows)

        avg_y = np.mean(y_vals)
        avg_x = np.mean(x_vals)
        
        if direction == Direction.RIGHT : avg_x = 640 - avg_x
        #print("avg_y : ", avg_y)
        #print("avg_x : ", avg_x)
        diff = avg_y + avg_x - (ImageTransformUtils.PIC_HEIGHT - 60) #ImageAlgorithms.threshold # was +40
        # thresholds : 
        # challenge 1 : 400
        # challenge 2 : 300
        # challenge 3 : 320
        differential_adjust = (diff - old_diff) * 0.25
        # kd was 0.25 for obstacles
        # kd was 1 for parking
        angle =  88 + direction.value * (int((diff) * 0.2) + differential_adjust)
        # kp was 0.2
        # kp was 0.75 for parking
        old_diff = diff
        #print("angle : ",angle)
        return angle

    @staticmethod
    def calculate_servo_angle_walls(img):
        angle1 = ImageAlgorithms.find_angle_from_img(img)
        angle = angle1
        if angle < 48:
            angle = 49
        elif angle > 128:
            angle = 127

        return int(angle)
    
    @staticmethod
    def find_obstacle_angle(obstacle_img, hsv_img, target_img, gray):
        global old_angle
        global old_is_green
        v1, v2, rect = ImageDrawingUtils.find_rect(obstacle_img, gray)
        if rect is None:
            return None, target_img, None
        x_center = rect[0][0] # + min(rect[1][0], rect[1][1])/2
        y_center = rect[0][1]

        if y_center > ImageTransformUtils.PIC_HEIGHT - 60:
            if y_center > ImageTransformUtils.PIC_HEIGHT - 30:
                return None, target_img, None
            else:
                return old_angle, None, old_is_green
        if y_center < 50:# was 60
            return None, target_img, None

        is_green = ImageColorUtils.is_rect_green(hsv_img, rect)

        if is_green:
            ImageDrawingUtils.draw_line(target_img, (x_center, y_center), (RIGHT_OBSTACLE_X_THRESHOLD, ImageTransformUtils.PIC_HEIGHT))
            rad_angle = math.atan2(y_center - ImageTransformUtils.PIC_HEIGHT, x_center - RIGHT_OBSTACLE_X_THRESHOLD)
        else:
            ImageDrawingUtils.draw_line(target_img, (x_center, y_center), (LEFT_OBSTACLE_X_THRESHOLD, ImageTransformUtils.PIC_HEIGHT))
            rad_angle = math.atan2(y_center - ImageTransformUtils.PIC_HEIGHT, x_center - LEFT_OBSTACLE_X_THRESHOLD)

        angle = 90 + math.degrees(rad_angle)
        old_angle = angle
        old_is_green = is_green
        return angle, target_img, is_green

    @staticmethod
    def calculate_servo_angle_obstacle(object_angle, is_green):
        if object_angle is None:
            return None
        #servo_angle = math.pow(object_angle * 0.1, 2) * 0.5
        if is_green:
            servo_angle = 88 - ((object_angle + 45) * 1.5) # green obstacle
        else:
            servo_angle = 88 - ((object_angle - 45) * 1.5) # red obstacle
        if servo_angle < 48:
            servo_angle = 49
        elif servo_angle > 128:
            servo_angle = 127
        return int(servo_angle)

    def choose_output_angle(angle_walls, angle_obstacles):
        if angle_obstacles is None:
            print("Walls at angle : ", angle_walls)
            return angle_walls
        print("Obstacles at angle : ", angle_obstacles)
        return angle_obstacles

    @staticmethod
    def get_top_angle(poly_lines):
        for i in range(len(poly_lines)):
            pt1 = poly_lines[i][0]
            pt2 = poly_lines[(i+1) % len(poly_lines)][0]
            dx = pt2[0] - pt1[0]
            dy = pt2[1] - pt1[1]
            angle = np.degrees(np.arctan2(dy,dx))
            if (angle > 178) or (angle < -178):
                print("Top wall angle = ", angle)
                return angle
        return None

    @staticmethod
    def calculate_servo_angle_parking(angle_walls, wall_angle):
        if wall_angle  is None:
            return None
        #servo_angle = math.pow(object_angle * 0.1, 2) * 0.5
        if wall_angle > 0:
            servo_angle = 88 - (wall_angle -180) * 10
        else:
            servo_angle = 88 - (wall_angle +180) * 10

        if servo_angle < 48:
            servo_angle = 49
        elif servo_angle > 128:
            servo_angle = 127
        return int(servo_angle)
    
    @staticmethod
    def get_starting_position(img):
        nbr_cols = 10
        mid_x = ImageTransformUtils.PIC_WIDTH // 2
        start = mid_x - (nbr_cols // 2)
        end = start + nbr_cols
        cols = range(start, end)
        
        distance = np.mean(ImageAlgorithms.find_black_from_bottom(img, cols))
        
        print("Wall distance = ", distance)
        
        if distance > START_WALL_HEIGHT_THRESHOLD:
            return StartPostition.BACK
