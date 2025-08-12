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
MIN_WIDTH = 5
MIN_HEIGHT = 5

COLOR_RANGES = {
    # this is hsv
    'blue': (np.array([100, 100, 50]), np.array([130, 255, 255])),
    'orange': (np.array([10, 100, 50]), np.array([30, 255, 255])),
    'all_colors': (np.array([0,100, 50]), np.array([179, 255, 255])),
    'green': (np.array([60, 100, 50]), np.array([80, 255, 255])),
    'red': (np.array([175, 100, 50]), np.array([185, 255, 255]))
}

class ImageUtils:

    CAMERA_PIC_WIDTH = 640                 # reduced image width
    CAMERA_PIC_HEIGHT = 360                # reduced image height
    PIC_WIDTH = 640
    PIC_HEIGHT = 280

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
    def calculate_color_mask(hsv_img, color):
        lower = COLOR_RANGES[color][0].copy()
        upper = COLOR_RANGES[color][1].copy()
        #print("lower,upper = ",lower, upper)
        if upper[0] > 179:
            #print("Lol")
            extra = upper[0] -179
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
    def remove_color(hsv_img, target_img, color):
        mask = ImageUtils.calculate_color_mask(hsv_img, color)
        target_img[mask > 0] = WHITE_COLOR  # Change color to white
        return target_img, mask
    
    @staticmethod
    def exclude_color(hsv_img, color):
        mask = cv2.bitwise_not(ImageUtils.calculate_color_mask(hsv_img, color))
        return mask
    
    @staticmethod
    def keep_color(img, color):
        mask = ImageUtils.calculate_color_mask(img, color)
             
        #dilated_mask = ImageUtils.dilate(mask)
        #keep_color_img = cv2.bitwise_and(img, img, mask=mask)
        #cv2.imshow("color Mask ", mask)
        return mask

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
    def find_contour(img, white = 0):
        contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None
        else:
            if white != 0:
                target_pt = (ImageUtils.PIC_WIDTH / 2, ImageUtils.PIC_HEIGHT - 10)
                contours = [cnt for cnt in contours if cv2.pointPolygonTest(cnt, target_pt, False) >= 0]
            if not contours:
                return
            biggest_contour = max(contours, key=cv2.contourArea)
        return biggest_contour
    
    @staticmethod
    def draw_polygon(binary_img, target_img):
        cnt = ImageUtils.find_contour(binary_img, 1)
        if cnt is None: return target_img, None
        epsilon = 0.01*cv2.arcLength(cnt, True)
        polygon = cv2.approxPolyDP(cnt, epsilon, True)
        mask = np.zeros_like(binary_img)
        cv2.fillPoly(mask, [polygon], (255, 255, 255))
        target_img = cv2.bitwise_and(binary_img, mask)        
        return target_img, polygon
    
    @staticmethod
    def find_rect(img, color_img = None):
        cnt = ImageUtils.find_contour(img)
        if cnt is None:
            return img, 360, None
        rect = cv2.minAreaRect(cnt)
        (w, h) = rect[1]
        if w < MIN_WIDTH or h < MIN_HEIGHT:
            return img, 360, None
        max_width_height = max(rect[1][0], rect[1][1])
        box = cv2.boxPoints(rect)
        box = np.intp(box)
        if color_img is not None:
            print("Dedans")
            x_coords = [pt[0] for pt in box]
            min_x = max(min(x_coords), 0)
            max_x = min(max(x_coords), img.shape[1] - 1)
            bottom_y = max(pt[1] for pt in box) # this finds the lowest point of the rect
            line_y = bottom_y + 2
            if line_y < img.shape[0]:
                white_line = color_img[int(line_y), int(min_x):int(max_x) + 1]    # creates line
                white_count = np.count_nonzero(white_line > 100)   # amount of white pixels
                total_count = white_line.size                       # amount of total pixels
                ratio = white_count / total_count
                print("White ratio : ", ratio)
                
                # Require at least 50% white pixels
                if ratio < 0.5:
                    print("Not enough white below")
                    return img, 360, None

        img_with_box = cv2.cvtColor(img.copy(), cv2.COLOR_GRAY2BGR)
        cv2.drawContours(img_with_box, [box], 0, (0, 255, 0), 2)
        return img_with_box, max_width_height, rect
    
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
    
    @staticmethod
    def draw_line(img, pt1, pt2):
        pt1 = (int(pt1[0]), int(pt1[1]))
        pt2 = (int(pt2[0]), int(pt2[1]))
        cv2.line(img, (pt1[0], pt1[1]), (pt2[0], pt2[1]), color=(0, 253, 0), thickness=3)
        cv2.imshow("Lines,", img)
    
    @staticmethod
    def find_color_from_pt(img, pt, color): # img is already given in hsv
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
        return ImageUtils.find_color_from_pt(img, pt, color)

    @staticmethod
    def is_rect_green(img, rect):
        return ImageUtils.find_color_from_rect(img, rect, 'green')