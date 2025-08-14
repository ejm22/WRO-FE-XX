from picamera2 import Picamera2
import time
from XX_2025_package.utils.image_transform_utils import ImageTransformUtils
from XX_2025_package.utils.image_transform_utils import ImageColorUtils
from XX_2025_package.classes.image_algoriths import ImageAlgorithms
import cv2
import numpy as np
from XX_2025_package.utils.enums import Color

class CameraManager:

    def __init__(self):
        self.picam2 = Picamera2()
        self.raw_image = None
        self.cropped_image = None
        self.colormask_image = None
        
        self.blue_mask = None
        self.orange_mask = None
        self.green_mask = None
        self.red_mask = None
        self.pink_mask = None
        self.blueline_image = None
        self.orangeline_image = None
        self.clean_blueline_image = None
        self.clean_orangeline_image = None
        self.cnt_blueline = None    # to delete and change place
        self.cnt_orangeline = None  # to delete and change place
        self.length_blue = None      # to delete and change place
        self.length_orange = None    # to delete and change place
        self.grayscale_image = None
        self.blurred_image = None
        self.binary_image = None
        self.clean_image = None
        self.polygon_image = None
        self.polygon_lines = None
        self.combined_mask = None
        self.grayscale_image = None
        self.binary_obstacle = None
        self.obstacle_image = None
        self.contour_obstacle = None
        self.pink_image = None

        self.configure_camera()

    def configure_camera(self):
        sensor_mode = self.picam2.sensor_modes[1]
        sensor_width, sensor_height = sensor_mode["size"]
        config = (self.picam2.create_still_configuration(
        raw={"size":(sensor_width,sensor_height)},
        main={"format":'RGB888',"size": (ImageTransformUtils.CAMERA_PIC_WIDTH, ImageTransformUtils.CAMERA_PIC_HEIGHT)}))
        self.picam2.configure(config)

    def start_camera(self):
        self.picam2.start()
        time.sleep(2)

    def capture_image(self):
        if self.raw_image is not None:
            del self.raw_image
        self.raw_image = self.picam2.capture_array()
        #cv2.imshow("Color", self.current_image)


    def transform_image(self):
        if self.raw_image is not None:
            self.cropped_image = ImageTransformUtils.crop_image(self.raw_image, 0, ImageTransformUtils.PIC_WIDTH, ImageTransformUtils.CAMERA_PIC_HEIGHT - ImageTransformUtils.PIC_HEIGHT, ImageTransformUtils.CAMERA_PIC_HEIGHT)
            self.hsv_image = ImageTransformUtils.bgr_to_hsv(self.cropped_image.copy())
            self.colormask_image,_ = ImageTransformUtils.remove_color(self.hsv_image.copy(), self.cropped_image.copy(), Color.ALL_COLORS)
            self.grayscale_image = ImageTransformUtils.color_to_grayscale(self.colormask_image)
            self.blurred_image = ImageTransformUtils.blur_image(self.grayscale_image)
            self.binary_image = ImageTransformUtils.make_binary(self.blurred_image)
            self.clean_image = ImageTransformUtils.clean_binary(self.binary_image)
            
            self.blue_mask = ImageColorUtils.calculate_color_mask(self.hsv_image, Color.BLUE)
            self.orange_mask = ImageColorUtils.calculate_color_mask(self.hsv_image, Color.ORANGE)
            self.green_mask = ImageColorUtils.calculate_color_mask(self.hsv_image, Color.GREEN)
            self.red_mask = ImageColorUtils.calculate_color_mask(self.hsv_image, Color.RED)
            self.pink_mask = ImageColorUtils.calculate_color_mask(self.hsv_image, Color.PINK)

            cv2.imshow("Green only", self.green_mask)
            self.polygon_image, self.polygon_lines = ImageTransformUtils.draw_polygon(self.clean_image, self.clean_image)
            self.blueline_image = ImageTransformUtils.keep_color(self.hsv_image, Color.BLUE)
            self.orangeline_image = ImageTransformUtils.keep_color(self.hsv_image, Color.ORANGE)
            self.clean_blueline_image = cv2.bitwise_and(self.blueline_image, self.blueline_image, mask = self.polygon_image)
            self.clean_orangeline_image = cv2.bitwise_and(self.orangeline_image, self.orangeline_image, mask = self.polygon_image)
            self.cnt_blueline, self.length_blue, _ = ImageTransformUtils.find_rect(self.clean_blueline_image)
            self.cnt_orangeline, self.length_orange, _ = ImageTransformUtils.find_rect(self.clean_orangeline_image)

            self.pink_image = cv2.bitwise_and(self.polygon_image, self.polygon_image, mask = self.pink_mask)
            self.combined_mask = cv2.bitwise_or(ImageTransformUtils.keep_color(self.hsv_image.copy(), Color.GREEN), ImageTransformUtils.keep_color(self.hsv_image.copy(), Color.RED))
            cv2.imshow("Combine_mask", self.combined_mask)
            cv2.imshow("img_polygon_image", self.polygon_image)
            self.obstacle_image = cv2.bitwise_and(self.polygon_image, self.polygon_image, mask = self.combined_mask)
            #self.binary_obstacle = cv2.bitwise_and(self.cropped_image.copy(), self.cropped_image.copy(), mask = self.combined_mask)
            #self.grayscale_image = ImageUtils.color_to_grayscale(self.binary_obstacle)
            #self.obstacle_image = ImageUtils.make_binary(self.grayscale_image)
            ##self.obstacle_image = ImageUtils.dilate(self.obstacle_image)
            self.contour_obstacle_with_rect, _, rect = ImageTransformUtils.find_rect(self.obstacle_image.copy(), self.grayscale_image.copy())

if __name__ == "__main__":
    camera_manager = CameraManager()
    camera_manager.start_camera()
    while True:
        camera_manager.capture_image()
        camera_manager.transform_image()
        cv2.imshow("Cropped image", camera_manager.cropped_image)
        cv2.imshow("Lol", camera_manager.obstacle_image)
        angle, image = ImageAlgorithms.find_obstacle_angle(camera_manager.obstacle_image.copy(), camera_manager.hsv_image.copy(), camera_manager.cropped_image.copy())
        cv2.imshow("Obstacle with rect", camera_manager.contour_obstacle_with_rect)
        
        #Test for keep red only
        #lowerdb = np.array([175, 100, 50])
        #upperdb = np.array([185, 255, 255])
        #if upperdb[0] > 179:
        #    extra = upperdb[0] -179
        #    upperdb[0] = 179
        #    mask1 = cv2.inRange(camera_manager.hsv_image, lowerdb, upperdb)
        #    lowerdb[0] = 0
        #    upperdb[0] = extra
        #    mask2 = cv2.inRange(camera_manager.hsv_image, lowerdb, upperdb)
        #    mask = cv2.bitwise_or(mask1, mask2)                    
        #    
        #else:
        #    mask = cv2.inRange(camera_manager.hsv_image, lowerdb, upperdb)
        #cv2.imshow("mask red cam", mask)
        #keep_red_image = cv2.bitwise_and(camera_manager.cropped_image.copy(), camera_manager.cropped_image.copy(), mask=mask )
        
        #cv2.imshow("Keep Red ", keep_red_image)
        #cv2.imshow("Blue mask", camera_manager.blue_mask)
        #cv2.imshow("Orange mask", camera_manager.orange_mask)
        #cv2.imshow("Green mask", camera_manager.green_mask)
        #cv2.imshow("Red mask", camera_manager.red_mask)
        
        # db part
        if image is not None:
            cv2.imshow("Image with line", image)

        print(angle)
        time.sleep(0.01)
        key = cv2.waitKey(1)  # Let OpenCV update the window
        if key == 27:  # Escape key to quit
            break