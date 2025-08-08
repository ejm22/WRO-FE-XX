from picamera2 import Picamera2
import time
from XX_2025_package.utils.image_utils import ImageUtils
from XX_2025_package.classes.image_algoriths import ImageAlgorithms
import cv2
import numpy as np

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

        self.configure_camera()

    def configure_camera(self):
        sensor_mode = self.picam2.sensor_modes[1]
        sensor_width, sensor_height = sensor_mode["size"]
        config = (self.picam2.create_still_configuration(
        raw={"size":(sensor_width,sensor_height)},
        main={"format":'RGB888',"size": (ImageUtils.CAMERA_PIC_WIDTH, ImageUtils.CAMERA_PIC_HEIGHT)}))
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
            self.cropped_image = ImageUtils.crop_image(self.raw_image, 0, ImageUtils.PIC_WIDTH, ImageUtils.CAMERA_PIC_HEIGHT - ImageUtils.PIC_HEIGHT, ImageUtils.CAMERA_PIC_HEIGHT)
            self.hsv_image = ImageUtils.bgr_to_hsv(self.cropped_image.copy())
            self.colormask_image,_ = ImageUtils.remove_color(self.hsv_image.copy(), self.cropped_image.copy(), 'all_colors')
            self.grayscale_image = ImageUtils.color_to_grayscale(self.colormask_image)
            self.blurred_image = ImageUtils.blur_image(self.grayscale_image)
            self.binary_image = ImageUtils.make_binary(self.blurred_image)
            self.clean_image = ImageUtils.clean_binary(self.binary_image)
            
            self.blue_mask = ImageUtils.calculate_color_mask(self.hsv_image, 'blue')
            self.orange_mask = ImageUtils.calculate_color_mask(self.hsv_image, 'orange')
            self.green_mask = ImageUtils.calculate_color_mask(self.hsv_image, 'green')
            self.red_mask = ImageUtils.calculate_color_mask(self.hsv_image, 'red')

            self.polygon_image, self.polygon_lines = ImageUtils.draw_polygon(self.clean_image, self.clean_image)
            self.blueline_image = ImageUtils.keep_color(self.hsv_image, 'blue')
            self.orangeline_image = ImageUtils.keep_color(self.hsv_image, 'orange')
            self.clean_blueline_image = cv2.bitwise_and(self.blueline_image, self.blueline_image, mask = self.polygon_image)
            self.clean_orangeline_image = cv2.bitwise_and(self.orangeline_image, self.orangeline_image, mask = self.polygon_image)
            self.cnt_blueline, self.length_blue, _ = ImageUtils.find_rect(self.clean_blueline_image)
            self.cnt_orangeline, self.length_orange, _ = ImageUtils.find_rect(self.clean_orangeline_image)

            self.combined_mask = cv2.bitwise_or(ImageUtils.keep_color(self.hsv_image.copy(), 'green'), ImageUtils.keep_color(self.hsv_image.copy(), 'red'))
            self.obstacle_image = cv2.bitwise_and(self.polygon_image, self.polygon_image, mask = self.combined_mask)
            #self.binary_obstacle = cv2.bitwise_and(self.cropped_image.copy(), self.cropped_image.copy(), mask = self.combined_mask)
            #self.grayscale_image = ImageUtils.color_to_grayscale(self.binary_obstacle)
            #self.obstacle_image = ImageUtils.make_binary(self.grayscale_image)
            ##self.obstacle_image = ImageUtils.dilate(self.obstacle_image)
            self.contour_obstacle_with_rect, _, rect = ImageUtils.find_rect(self.obstacle_image.copy())

if __name__ == "__main__":
    camera_manager = CameraManager()
    camera_manager.start_camera()
    while True:
        camera_manager.capture_image()
        camera_manager.transform_image()
        #cv2.imshow("Raw image", camera_manager.raw_image)
        cv2.imshow("Cropped image", camera_manager.cropped_image)
        #cv2.imshow("Masked image", camera_manager.colormask_image)
        #cv2.imshow("Blue line only", camera_manager.clean_blueline_image)
        #cv2.imshow("Orange line only", camera_manager.clean_orangeline_image)
        #if camera_manager.cnt_blueline is not None:
        #    cv2.imshow("Cnt blue", camera_manager.cnt_blueline)
        #if camera_manager.cnt_orangeline is not None:
        #    cv2.imshow("Cnt orange", camera_manager.cnt_orangeline)
        #if (camera_manager.length_blue > camera_manager.length_orange):
        #    print("blue")
        #else:
        #    print("orange")
        #print(camera_manager.length_blue)
        #print(camera_manager.length_orange)
        #cv2.imshow("Grayscale image", camera_manager.grayscale_image)
        #cv2.imshow("Blurred image", camera_manager.blurred_image)
        #cv2.imshow("Binary image", camera_manager.binary_image)
        #cv2.imshow("Clean image", camera_manager.clean_image)
        #cv2.imshow("x image", camera_manager.polygon_image)
        #cv2.imshow("Binary obstacle image", camera_manager.binary_obstacle)
        #cv2.imshow("Obstacle image", camera_manager.obstacle_image)
        #cv2.imshow("Big obstacle", camera_manager.contour_obstacle_with_rect)
        #cv2.imshow("Combined mask", camera_manager.combined_mask)
        cv2.imshow("Lol", camera_manager.obstacle_image)
        angle, image = ImageAlgorithms.find_obstacle_angle(camera_manager.obstacle_image.copy(), camera_manager.hsv_image.copy(), camera_manager.cropped_image.copy())
        cv2.imshow("Obstacle with rect", camera_manager.contour_obstacle_with_rect)
        #Test for keep red only
        lowerdb = np.array([175, 100, 50])
        upperdb = np.array([185, 255, 255])
        if upperdb[0] > 179:
            extra = upperdb[0] -179
            upperdb[0] = 179
            mask1 = cv2.inRange(camera_manager.hsv_image, lowerdb, upperdb)
            lowerdb[0] = 0
            upperdb[0] = extra
            mask2 = cv2.inRange(camera_manager.hsv_image, lowerdb, upperdb)
            mask = cv2.bitwise_or(mask1, mask2)                    
            
        else:
            mask = cv2.inRange(camera_manager.hsv_image, lowerdb, upperdb)
        #cv2.imshow("mask red cam", mask)
        keep_red_image = cv2.bitwise_and(camera_manager.cropped_image.copy(), camera_manager.cropped_image.copy(), mask=mask )
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