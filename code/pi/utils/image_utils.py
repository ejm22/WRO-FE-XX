import numpy as np
import cv2
from picamera2 import Picamera2


BLUR_FILTER_SIZE = 9            # size of the bilateral filter
BLUR_SIGMA_COLOR = 75           # how much colors can differ to be considered similar
BLUR_SIGMA_SPACE = 75           # how far pixels can be to influence each other
THRESHOLD = 100                 # threshold value for binary image
WHITE_VALUE = 255               # to set white color in binary image
WHITE_COLOR = (255, 255, 255)   # BGR white color for OpenCV
MATRIX_SIZE = 5                 # size of the kernel for morphological operations

COLOR_RANGES = {
    'blue': (np.array([100, 100, 50]), np.array([130, 255, 255])),
    # Add other colors if needed, next is orange
}

class ImageUtils:

    PIC_WIDTH = 640                 # reduced image width
    PIC_HEIGHT = 360                # reduced image height

    @staticmethod
    def find_black_from_bottom(img, col_range):
            y_vals = []
            for x in col_range:
                for y in reversed(range(ImageUtils.PIC_HEIGHT)):
                    if img[y,x] == 0:
                        y_vals.append(y)
                        break
                else:
                    y_vals.append(0)
            return y_vals
    
    def find_black_from_middle_left(img, row_range):
        x_vals = []
        for y in row_range:
            for x in reversed(range(ImageUtils.PIC_WIDTH // 2)):
                if img[y,x] == 0:
                    x_vals.append(x)
                    break
            else:
                x_vals.append(0)
        return x_vals
    
    def find_black_from_middle_right(img, row_range):
        x_vals = []
        for y in row_range:
            for x in range(ImageUtils.PIC_WIDTH // 2):
                if img[y,x] == 0:
                    x_vals.append(x)
                    break
            else:
                x_vals.append(0)
        return x_vals

    @staticmethod
    def crop_image(img, x_start, x_end, y_start, y_end):
        return img[y_start:y_end, x_start:x_end]

    @staticmethod
    def bgr_to_hsv(img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    @staticmethod
    def remove_color(img, color):
        lower, upper = COLOR_RANGES[color]
        mask = cv2.inRange(ImageUtils.bgr_to_hsv(img), lower, upper)
        img[mask > 0] = WHITE_COLOR  # Change color to white
        return img

    @staticmethod
    def color_to_grayscale(img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def blur_image(img):
        return cv2.bilateralFilter(img, BLUR_FILTER_SIZE, BLUR_SIGMA_COLOR, BLUR_SIGMA_SPACE)

    @staticmethod
    def make_binary(img):
        _, binary_img = cv2.threshold(img, THRESHOLD, WHITE_VALUE, cv2.THRESH_BINARY)  # Invert threshold
        return binary_img

    @staticmethod
    def clean_binary(img):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    
    @staticmethod
    def visualize_contour(img):
        contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        white_zone_contour = max(contours, key=cv2.contourArea)
        visualized = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(visualized, [white_zone_contour], -1, (0,255,0), 2)  # Green contour, thickness 2
        return visualized
    
    @staticmethod
    def find_angle_from_img(img, nbr_cols = 10):
        bottom_rows = range(ImageUtils.PIC_HEIGHT - 10, ImageUtils.PIC_HEIGHT)
        left_cols = range(0, nbr_cols)
        right_cols = range(ImageUtils.PIC_WIDTH - nbr_cols, ImageUtils.PIC_WIDTH)

        left_y_vals = ImageUtils.find_black_from_bottom(img, left_cols)
        right_y_vals = ImageUtils.find_black_from_bottom(img, right_cols)

        avg_left_y = np.mean(left_y_vals)
        avg_right_y = np.mean(right_y_vals)

        if avg_left_y > 350:
            left_y_vals = ImageUtils.find_black_from_middle_left(img, bottom_rows)
            print(left_y_vals)
            new_avg_left_y = np.mean(left_y_vals)
            if new_avg_left_y > 10:
                avg_left_y = avg_left_y + new_avg_left_y // 4
        
        if avg_right_y > 350:
            right_y_vals = ImageUtils.find_black_from_middle_right(img, bottom_rows)
            print(right_y_vals)
            new_avg_right_y = np.mean(right_y_vals)
            if new_avg_right_y < 630:
                avg_right_y = avg_right_y + (640 - new_avg_right_y) // 4

        angle = 88 - (int((avg_left_y - avg_right_y) / 7))
        if angle < 48:
            angle = 49
        elif angle > 138:
            angle = 137
        return angle
