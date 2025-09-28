import numpy as np
import cv2
from XX_2025_package.utils.enums import Color

COLOR_RANGES = {
    Color.BLUE: (np.array([100, 60, 50]), np.array([130, 255, 255])),
    Color.ORANGE: (np.array([6, 60, 50]), np.array([30, 255, 255])),
    Color.ALL_COLORS: (np.array([0, 100, 50]), np.array([179, 255, 255])),
    Color.GREEN: (np.array([60, 100, 50]), np.array([85, 255, 255])),
    Color.RED: (np.array([175, 100, 50]), np.array([184, 210, 255])),
    Color.PINK: (np.array([155, 135, 50]), np.array([172, 255, 255])),
    Color.WHITE: (np.array([0, 0, 100]), np.array([179, 30, 255])),
}

class ImageColorUtils:
    @staticmethod
    def calculate_color_mask(hsv_img, color):
        """
        Generate a binary mask for the specified color in an HSV image.

        I/O:
            hsv_img (np.ndarray): The input HSV image.
            color (Color): The color to detect (must be a key in COLOR_RANGES).
            returns: np.ndarray: A binary mask where the specified color is white (255) and all else is black (0).
        """
        lower = COLOR_RANGES[color][0].copy()
        upper = COLOR_RANGES[color][1].copy()
        if upper[0] > 179:
            extra = upper[0] - 179
            upper[0] = 179
            mask1 = cv2.inRange(hsv_img, lower, upper)
            lower[0] = 0
            upper2 = np.array([extra, upper[1], upper[2]])
            mask2 = cv2.inRange(hsv_img, lower, upper2)
            mask = cv2.bitwise_or(mask1, mask2)
        else:
            mask = cv2.inRange(hsv_img, lower, upper)
        return mask

    @staticmethod
    def is_color_at_point(img, pt, color):
        """
        img: HSV image
        pt: (x, y) point
        color: string, one of the keys in COLOR_RANGES
        return: bool, True if the color at pt matches the specified color
        """
        lower, higher = COLOR_RANGES[color]
        x, y = map(int, pt)
        hsv_value = img[y, x]
        pixel = np.uint8([[hsv_value]])
        return cv2.inRange(pixel, lower, higher)[0] == 255
    
    @staticmethod
    def find_color_from_pt(img, pt):
        """
        img: HSV image
        pt: (x, y) point
        
        return: color if a color is detected at pt, else None
        """
        print("find color")
        x, y = map(int, pt)
        hsv_value = img[x, y]
        pixel = np.uint8([[hsv_value]])
        for color, (lower, upper) in COLOR_RANGES.items():
            if cv2.inRange(pixel, lower, upper)[0] == 255:
                print(color)
                return color
        

    @staticmethod
    def find_color_from_rect(img, rect, color):
        x_center = rect[0][0]
        y_center = rect[0][1]
        pt = (x_center, y_center)
        return ImageColorUtils.is_color_at_point(img, pt, color)
    
    @staticmethod
    def is_rect_green(img, rect):
        return ImageColorUtils.find_color_from_rect(img, rect, Color.GREEN)