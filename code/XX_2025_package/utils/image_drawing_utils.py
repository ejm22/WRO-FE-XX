import cv2
from utils.image_transform_utils import ImageTransformUtils
import numpy as np
from classes.context_manager import ContextManager

MIN_WIDTH = 13
MIN_HEIGHT = 13

class ImageDrawingUtils:

    @staticmethod
    def add_text_to_image(image, text, position=(50, 50), color=(255, 255, 255)):
        """
        Add text to an image.

        Parameters:
            image, text to add, position (tuple), color (rgb format).

        Returns:
            The image with the text added.
        """
        if image is not None:
            cv2.putText(image, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
        return image
    
    @staticmethod
    def find_contour(img, white = 0):
        """
        Finds the biggest and second biggest contour in a binary image.
        I/O:
            img: binary image
            white: if 1, only contours containing the bottom center point are considered
            returns: biggest contour, second biggest contour (or None if not found)
        """
        contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if white == 1:
            target_pt = (ImageTransformUtils.PIC_WIDTH / 2, ImageTransformUtils.PIC_HEIGHT - 10)
            contours = [cnt for cnt in contours if cv2.pointPolygonTest(cnt, target_pt, False) >= 0]
        if not contours:
            return None, None
        biggest_contour = max(contours, key=cv2.contourArea)
        contours = [cnt for cnt in contours if not np.array_equal(cnt, biggest_contour)]
        if not contours:
            return biggest_contour, None
        second_biggest_contour = max(contours, key=cv2.contourArea)
        return biggest_contour, second_biggest_contour

    @staticmethod
    def draw_polygon(binary_img, target_img):
        """
        Finds a polygon in the binary image and draws it on the target image.
        I/O:
            binary_img: binary image to find the polygon in
            target_img: image to draw the polygon on
            returns: target_img with polygon drawn, polygon points (or None if not found)
        """
        cnt, _ = ImageDrawingUtils.find_contour(binary_img, 1)
        if cnt is None: return target_img, None
        epsilon = 0.001*cv2.arcLength(cnt, True)  # was 0.004
        polygon = cv2.approxPolyDP(cnt, epsilon, True)
        mask = np.zeros_like(binary_img)
        cv2.fillPoly(mask, [polygon], (255, 255, 255))
        target_img = cv2.bitwise_and(binary_img, mask)
        return target_img, polygon
    
    @staticmethod
    def find_rect(img, binary_img = None, target_img = None):
        """
        Finds a rectangle in the image. Can add target_img to draw it on an image
        """
        cnt, cnt2 = ImageDrawingUtils.find_contour(img)
        if cnt is None:
            return img, 0, None, None
        rect1 = cv2.minAreaRect(cnt)
        rect2 = None
        if cnt2 is not None:
            rect2 = cv2.minAreaRect(cnt2)
            (w2, h2) = rect2[1]
            if w2 < MIN_WIDTH or h2 < MIN_HEIGHT:
                rect2 = None
        (w1, h1) = rect1[1]
        if ContextManager.CHALLENGE == 2 or ContextManager.CHALLENGE == 4:
            if w1 < MIN_WIDTH or h1 < MIN_HEIGHT:
                return img, 0, None, None
        max_width_height = max(rect1[1][0], rect1[1][1])
        box = cv2.boxPoints(rect1)
        box = np.intp(box)
        if binary_img is not None:
            x_coords = [pt[0] for pt in box]
            min_x = max(min(x_coords), 0)
            max_x = min(max(x_coords), img.shape[1] - 1)
            bottom_y = max(pt[1] for pt in box) # this finds the lowest point of the rect
            line_y = bottom_y + 20 # was 2
            if line_y < img.shape[0]:
                white_line = binary_img[int(line_y), int(min_x):int(max_x) + 1]    # creates line
                white_count = np.count_nonzero(white_line == 255)   # amount of white pixels
                total_count = white_line.size                       # amount of total pixels
                ratio = white_count / total_count
                # Require at least 50% white pixels
                if ratio < 0.5:
                    return img, 0, None, None
        img_with_box = cv2.cvtColor(img.copy(), cv2.COLOR_GRAY2BGR)
        cv2.drawContours(img_with_box, [box], 0, (0, 255, 0), 2)
        if target_img is not None:
            cv2.drawContours(target_img, [box], 0, (168, 116, 251), 2)
        return img_with_box, max_width_height, rect1, rect2
    
    @staticmethod
    def draw_line(img, pt1, pt2):
        pt1 = (int(pt1[0]), int(pt1[1]))
        pt2 = (int(pt2[0]), int(pt2[1]))
        cv2.line(img, (pt1[0], pt1[1]), (pt2[0], pt2[1]), color=(0, 253, 0), thickness=3)
        #cv2.imshow("Lines,", img)

    @staticmethod
    def draw_circle(img, center, radius, color = (255, 255, 255)):
        cv2.circle(img, center, radius, color, thickness = 3)

    @staticmethod
    def draw_contour(img, contour, color = (255, 255, 255)):
        cv2.drawContours(img, [contour], -1, color, 2)