from picamera2 import Picamera2
import time
from XX_2025_package.utils.image_utils import ImageUtils
import cv2

class CameraManager:

    def __init__(self):
        self.picam2 = Picamera2()
        self.raw_image = None
        self.cropped_image = None
        self.colormask_image = None
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
        if self.raw_image is not None:
            del self.raw_image
        self.raw_image = self.picam2.capture_array()
        #cv2.imshow("Color", self.current_image)


    def transform_image(self):
        if self.raw_image is not None:
            self.cropped_image = ImageUtils.crop_image(self.raw_image, 0, ImageUtils.PIC_WIDTH, 0, ImageUtils.PIC_HEIGHT)
            self.colormask_image,_ = ImageUtils.remove_color(self.cropped_image.copy(), 'all_colors')
            self.grayscale_image = ImageUtils.color_to_grayscale(self.colormask_image)
            self.blurred_image = ImageUtils.blur_image(self.grayscale_image)
            self.binary_image = ImageUtils.make_binary(self.blurred_image)
            self.clean_image = ImageUtils.clean_binary(self.binary_image)
            self.polygon_image,self.polygon_lines = ImageUtils.draw_polygon(self.clean_image, self.clean_image)
            self.blueline_image = ImageUtils.keep_color(self.cropped_image, 'blue')
            self.orangeline_image = ImageUtils.keep_color(self.cropped_image, 'orange')
            self.clean_blueline_image = cv2.bitwise_and(self.blueline_image, self.blueline_image, mask = self.polygon_image)
            self.clean_orangeline_image = cv2.bitwise_and(self.orangeline_image, self.orangeline_image, mask = self.polygon_image)
            self.cnt_blueline, self.length_blue = ImageUtils.find_rect(self.clean_blueline_image)
            self.cnt_orangeline, self.length_orange = ImageUtils.find_rect(self.clean_orangeline_image)

if __name__ == "__main__":
    camera_manager = CameraManager()
    camera_manager.start_camera()
    while True:
        camera_manager.capture_image()
        camera_manager.transform_image()
        cv2.imshow("Raw image", camera_manager.raw_image)
        cv2.imshow("Cropped image", camera_manager.cropped_image)
        cv2.imshow("Masked image", camera_manager.colormask_image)
        cv2.imshow("Blue line only", camera_manager.clean_blueline_image)
        cv2.imshow("Orange line only", camera_manager.clean_orangeline_image)
        if camera_manager.cnt_blueline is not None:
            cv2.imshow("Cnt blue", camera_manager.cnt_blueline)
        if camera_manager.cnt_orangeline is not None:
            cv2.imshow("Cnt orange", camera_manager.cnt_orangeline)
        if (camera_manager.length_blue > camera_manager.length_orange):
            print("blue")
        else:
            print("orange")
        print(camera_manager.length_blue)
        print(camera_manager.length_orange)
        cv2.imshow("Grayscale image", camera_manager.grayscale_image)
        cv2.imshow("Blurred image", camera_manager.blurred_image)
        cv2.imshow("Binary image", camera_manager.binary_image)
        cv2.imshow("Clean image", camera_manager.clean_image)
        cv2.imshow("x image", camera_manager.polygon_image)
        time.sleep(0.01)
        key = cv2.waitKey(1)  # Let OpenCV update the window
        if key == 27:  # Escape key to quit
            break