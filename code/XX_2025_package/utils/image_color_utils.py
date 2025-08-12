import numpy as np
import cv2

COLOR_RANGES = {
    'blue': (np.array([100, 100, 50]), np.array([130, 255, 255])),
    'orange': (np.array([10, 100, 50]), np.array([30, 255, 255])),
    'all_colors': (np.array([0, 100, 50]), np.array([179, 255, 255])),
    'green': (np.array([60, 100, 50]), np.array([80, 255, 255])),
    'red': (np.array([175, 100, 50]), np.array([185, 255, 255])),
    'pink': (np.array([155, 135, 50]), np.array([175, 255, 255]))
}

class ImageColorUtils:
    @staticmethod
    def calculate_color_mask(hsv_img, color):
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
    def find_color_from_pt(img, pt, color):
        lower, higher = COLOR_RANGES[color]
        x, y = map(int, pt)
        hsv_value = img[y, x]
        pixel = np.uint8([[hsv_value]])
        return cv2.inRange(pixel, lower, higher)[0] == 255

    @staticmethod
    def find_color_from_rect(img, rect, color):
        x_center = rect[0][0]
        y_center = rect[0][1]
        pt = (x_center, y_center)
        return ImageColorUtils.find_color_from_pt(img, pt, color)
    
    @staticmethod
    def is_rect_green(img, rect):
        return ImageColorUtils.find_color_from_rect(img, rect, 'green')