from picamera2 import Picamera2
import time
from XX_2025_package.utils.image_transform_utils import ImageTransformUtils
from XX_2025_package.utils.image_transform_utils import ImageColorUtils
import cv2
import numpy as np
from XX_2025_package.utils.enums import Color
from XX_2025_package.utils.image_drawing_utils import ImageDrawingUtils
import math
import os
from XX_2025_package.video.video_counter import VideoCounter

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
        self.with_pink_combined_mask = None
        self.grayscale_image = None
        self.binary_obstacle = None
        self.obstacle_image = None
        self.pink_obstacle_image = None
        self.contour_obstacle = None
        self.pink_image = None
        
        # the image used to display all the relevant info
        self.display_image = None

        self.configure_camera()

    def configure_camera(self):
        sensor_mode = self.picam2.sensor_modes[1]
        sensor_width, sensor_height = sensor_mode["size"]
        config = (self.picam2.create_still_configuration(
        raw={"size":(sensor_width,sensor_height)},
        main={"format":'RGB888',"size": (ImageTransformUtils.CAMERA_PIC_WIDTH, ImageTransformUtils.CAMERA_PIC_HEIGHT)}))
        self.picam2.configure(config)
        
        self.conficure_video_output()
        
    def configure_video_output(self):
        output_folder = os.path.join(os.path.dirname(__file__), "../video")
        os.makedirs(output_folder, exist_ok=True)
        
        output_path = os.path.join(output_folder, f"video{VideoCounter.get_video_counter()}.mp4")
        
        fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        self.video_output = cv2.VideoWriter(output_path, fourcc, 20.0, (ImageTransformUtils.PIC_WIDTH, ImageTransformUtils.PIC_HEIGHT))
        VideoCounter.increment_video_counter()
        
    def start_camera(self):
        self.picam2.start()
        time.sleep(2)

    def capture_image(self):
        if self.raw_image is not None:
            del self.raw_image
        self.raw_image = self.picam2.capture_array()
        
    def add_frame_to_video(self):
        if self.video_output is None:
            return
        if self.display_image.shape[1] != ImageTransformUtils.PIC_WIDTH or self.display_image.shape[0] != ImageTransformUtils.PIC_HEIGHT:
            print(f"Frame size does not match video output size. Expected ({ImageTransformUtils.PIC_WIDTH}, {ImageTransformUtils.PIC_HEIGHT}), got {self.display_image.shape[1]}x{self.display_image.shape[0]}.")
            return
        self.video_output.write(self.display_image)


    def transform_image(self):
        if self.raw_image is not None:
            self.cropped_image = ImageTransformUtils.crop_image(self.raw_image, 0, ImageTransformUtils.PIC_WIDTH, ImageTransformUtils.CAMERA_PIC_HEIGHT - ImageTransformUtils.PIC_HEIGHT, ImageTransformUtils.CAMERA_PIC_HEIGHT)
            self.display_image = self.cropped_image.copy()
            
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

            self.polygon_image, self.polygon_lines = ImageDrawingUtils.draw_polygon(self.clean_image, self.clean_image)
            self.blueline_image = ImageTransformUtils.keep_color(self.hsv_image, Color.BLUE)
            self.orangeline_image = ImageTransformUtils.keep_color(self.hsv_image, Color.ORANGE)
            self.clean_blueline_image = cv2.bitwise_and(self.blueline_image, self.blueline_image, mask = self.polygon_image)
            self.clean_orangeline_image = cv2.bitwise_and(self.orangeline_image, self.orangeline_image, mask = self.polygon_image)
            self.cnt_blueline, self.length_blue, _ = ImageDrawingUtils.find_rect(self.clean_blueline_image)
            self.cnt_orangeline, self.length_orange, _ = ImageDrawingUtils.find_rect(self.clean_orangeline_image)

            #self.pink_image = cv2.bitwise_and(self.polygon_image, self.polygon_image, mask = self.pink_mask)
            self.combined_mask = cv2.bitwise_or(ImageTransformUtils.keep_color(self.hsv_image.copy(), Color.GREEN), ImageTransformUtils.keep_color(self.hsv_image.copy(), Color.RED))
            cv2.imshow("img_polygon_image", self.polygon_image)
            self.obstacle_image = cv2.bitwise_and(self.polygon_image, self.polygon_image, mask = self.combined_mask)
            
            #self.binary_obstacle = cv2.bitwise_and(self.cropped_image.copy(), self.cropped_image.copy(), mask = self.combined_mask)
            #self.grayscale_image = ImageUtils.color_to_grayscale(self.binary_obstacle)
            #self.obstacle_image = ImageUtils.make_binary(self.grayscale_image)
            ##self.obstacle_image = ImageUtils.dilate(self.obstacle_image)
            ImageDrawingUtils.find_rect(self.pink_mask.copy(), self.polygon_image.copy(), self.display_image)
            ImageDrawingUtils.find_rect(self.obstacle_image.copy(), self.polygon_image.copy(), self.display_image)
    
    def draw_arc(self, image, servo_angle):# Define arc parameters
 
        # Parameters
        wheelbase = .165  # m
        steering_angle_deg = servo_angle  # degrees
        steering_angle_rad = math.radians(steering_angle_deg)
        path_length = .3 # m

        # Calculate turning radius
        R = wheelbase / math.tan(steering_angle_rad)

        # Generate arc points in world coordinates
        points_world = []
        for d in np.linspace(0, path_length, num=50):
            x = R * math.sin(d / R)
            y = R * (1 - math.cos(d / R))
            points_world.append([x, y])
            print(x,y)

        points_world = np.array(points_world)

        # Simplified projection: scale and shift to image coordinates
        # These values depend on your camera setup
        scale = 1000  # pixels per meter
        if servo_angle < 0: 
            offset_x, offset_y = 320, 400  # image center or bottom center

        else:
            offset_x, offset_y = 320, 400  # image center or bottom center

        # Rotate to match image orientation (forward = up)
        points_world_rotated = np.array([[-p[1], p[0]] for p in points_world])

        # Project to image coordinates
        points_image = np.array([
                [int(offset_x + p[0]*scale), int(offset_y - p[1]*scale)]
        for p in points_world_rotated])

        # Draw path
        cv2.polylines(image, [points_image], isClosed=False, color=(0, 255, 0), thickness=2)

        cv2.imshow("Projected Path", image)



if __name__ == "__main__":
    camera_manager = CameraManager()
    camera_manager.start_camera()
    while True:
        camera_manager.capture_image()
        camera_manager.transform_image()
        for i in range (41, -41, -6):
            camera_manager.draw_arc(camera_manager.cropped_image, i)
        #    time.sleep(.5)
        cv2.imshow("Lol", camera_manager.obstacle_image)

        time.sleep(0.01)
        key = cv2.waitKey(1)  # Let OpenCV update the window
        if key == 27:  # Escape key to quit
            break