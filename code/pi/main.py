import cv2
import serial
import time
from classes.camera_manager import CameraManager
from utils.image_utils import ImageUtils

arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)

if __name__ == "__main__":
    camera_manager = CameraManager()
    camera_manager.start_camera()
    cv2.namedWindow("White Zone", cv2.WINDOW_AUTOSIZE)

    while True:
        line = arduino.readline()
        camera_manager.capture_image()
        img = camera_manager.transform_image()
        cv2.imshow("White Zone", img)

        if arduino.out_waiting == 0:
            print(f"Trying to send")
            command = f"{ImageUtils.find_angle_from_img(img)},3000.".encode()
            arduino.write(command)
            arduino.flush()
            print(f"Sent command: {command.decode().strip()}")

        else:
            print("Arduino is busy, skipping command.")
        #arduino.write(f"{ImageUtils.find_angle_from_img(img)},3000.".encode())
        del img  # Free memory
        time.sleep(0.1)
        key = cv2.waitKey(1)  # Let OpenCV update the window
        if key == 27:  # Escape key to quit
            break