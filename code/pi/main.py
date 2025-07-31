import cv2
import serial
import time
from classes.camera_manager import CameraManager
from utils.image_utils import ImageUtils

arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=1)


if __name__ == "__main__":
    print("Hello")
    camera_manager = CameraManager()
    camera_manager.start_camera()

    while True:
        camera_manager.capture_image()
        time.sleep(1)
        img = camera_manager.transform_image()
        cv2.imshow("White Zone", img)
  
        arduino.write(f"{ImageUtils.find_angle_from_img(img)},3000.".encode())
        time.sleep(0.1)
        key = cv2.waitKey(1)  # Let OpenCV update the window
        if key == 27:  # Escape key to quit
            break
