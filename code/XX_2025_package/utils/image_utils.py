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
    'orange': (np.array([0, 100, 50]), np.array([30, 255, 255])),
    'all_colors': (np.array([0,100, 50]), np.array([179, 255, 255])),
    # Add other colors if needed, next is orange
}

class ImageUtils:

    PIC_WIDTH = 640                 # reduced image width
    PIC_HEIGHT = 360                # reduced image height

    @staticmethod
    def crop_image(img, x_start, x_end, y_start, y_end):
        return img[y_start:y_end, x_start:x_end]

    @staticmethod
    def bgr_to_hsv(img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    def dilate(img):
        kernel = np.ones((3,3), np.uintp)
        dilated_image = cv2.dilate(img, kernel, iterations = 3)
        return dilated_image

    @staticmethod
    def remove_color(img, color):
        lower, upper = COLOR_RANGES[color]
        mask = cv2.inRange(ImageUtils.bgr_to_hsv(img), lower, upper)
        cv2.imshow("Mask", mask)
        img[mask > 0] = WHITE_COLOR  # Change color to white
        return img, mask
    
    def keep_color(img, color):
        lower, upper = COLOR_RANGES[color]
        mask = cv2.inRange(ImageUtils.bgr_to_hsv(img), lower, upper)
        dilated_mask = ImageUtils.dilate(mask)
        #cv2.imshow("Mask keep", mask)
        #keep_color_img = cv2.bitwise_and(img, img, mask=mask)
        return dilated_mask

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
    def find_contour(img):
        contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None
        else:
            white_zone_contour = max(contours, key=cv2.contourArea)
        return white_zone_contour
    
    @staticmethod
    def draw_polygon(binary_img, target_img):
        cnt = ImageUtils.find_contour(binary_img)
        epsilon = 0.01*cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        mask = np.zeros_like(binary_img)
        cv2.fillPoly(mask, [approx], (255, 255, 255))
        target_img = cv2.bitwise_and(binary_img, mask)        
        return target_img, approx
    
    def find_rect(img):
        cnt = ImageUtils.find_contour(img)
        if cnt is None:
            return None, 360
        rect = cv2.minAreaRect(cnt)
        max_width_height = max(rect[1][0], rect[1][1])
        box = cv2.boxPoints(rect)
        box = np.intp(box)
        img_with_box = cv2.cvtColor(img.copy(), cv2.COLOR_GRAY2BGR)
        cv2.drawContours(img_with_box, [box], 0, (0, 255, 0), 2)
        return img_with_box, max_width_height
    
    @staticmethod
    def get_top_line_coords(binary_img):
        cnt = ImageUtils.find_contour(binary_img)
        epsilon = 0.01*cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        for i in range(len(approx)):
            pt1 = approx[i][0]
            pt2 = approx[(i+1) % len(approx)][0]
            dx = pt2[0] - pt1[0]
            dy = pt2[1] - pt1[1]
            angle = np.degrees(np.arctan2(dy,dx))
            if abs(angle) > 175:
                return [pt1.tolist(), pt2.tolist()]
        return None

    @staticmethod
    def get_corner_line_coords(binary_img):
        cnt = ImageUtils.find_contour(binary_img)
        epsilon = 0.01*cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        for i in range(len(approx)):
            pt1 = approx[i][0]
            pt2 = approx[(i+1) % len(approx)][0]
            dx = pt2[0] - pt1[0]
            dy = pt2[1] - pt1[1]
            angle = np.degrees(np.arctan2(dy,dx))
            #print("Angle corner = ", angle)
            if (angle > 50) & (angle < 85):
                return [pt1.tolist(), pt2.tolist()]
        return None
