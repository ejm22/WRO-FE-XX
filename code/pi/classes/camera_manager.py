from picamera2 import Picamera2
import time
from utils.image_utils import ImageUtils
import cv2

class CameraManager:

    def __init__(self):
        self.picam2 = Picamera2()
        self.current_image = None
        self.cropped_image = None
        self.colormask_image = None
        self.grayscale_image = None
        self.blurred_image = None
        self.binary_image = None
        self.clean_image = None
        self.soundproof_image = None

        self.configure_camera()

    def configure_camera(self):
        sensor_mode = self.picam2.sensor_modes[1]
        sensor_width, sensor_height = sensor_mode["size"]
        config = (self.picam2.create_still_configuration(
        raw={"size":(sensor_width,sensor_height)},
        main={"format":'RGB888',"size": (ImageUtils.PIC_WIDTH, ImageUtils.PIC_HEIGHT)}))
        self.picam2.configure(config)

    def start_camera(self):
        self.picam2.start()
        time.sleep(2)

    def capture_image(self):
        if self.current_image is not None:
            del self.current_image
        self.current_image = self.picam2.capture_array()
        #cv2.imshow("Color", self.current_image)


    def transform_image(self):
        if self.current_image is not None:
            self.cropped_image = ImageUtils.crop_image(self.current_image.copy(), 0, ImageUtils.PIC_WIDTH, 0, ImageUtils.PIC_HEIGHT)
            #cv2.imshow("Captured Image", img)
            #input("Press Enter to continue...")
            self.colormask_image = ImageUtils.remove_color(self.cropped_image.copy(), 'blue_orange')
            #cv2.imshow("No Blue", img)
            #input("Press Enter to continue...")
            img = ImageUtils.color_to_grayscale(self.colormask_image.copy())
            #cv2.imshow("Grayscale Image", img)
            #input("Press Enter to continue...")
            img = ImageUtils.blur_image(img.copy())
            img = ImageUtils.make_binary(img.copy())
            img = ImageUtils.clean_binary(img.copy())
            self.soundproof_image,_ = ImageUtils.draw_polygon(img.copy(), img.copy())
            #img = ImageUtils.visualize_contour(img)
            
            return self.soundproof_image, self.colormask_image