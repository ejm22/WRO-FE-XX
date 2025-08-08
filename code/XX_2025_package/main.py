import cv2
import serial
import time
from XX_2025_package.classes.camera_manager import CameraManager
from XX_2025_package.utils.image_utils import ImageUtils
from XX_2025_package.classes.image_algoriths import ImageAlgorithms

arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)
speed = 5500

if __name__ == "__main__":
    time.sleep(1)
    camera_manager = CameraManager()
    camera_manager.start_camera()
    #cv2.namedWindow("White Zone", cv2.WINDOW_AUTOSIZE)
    arduino.write(b'v')
    time.sleep(0.1)
    line=arduino.readline().decode().strip()
    if line:
        print(line)
    i=0
    camera_manager.capture_image()
    camera_manager.transform_image()
    dir = ImageAlgorithms.get_direction(camera_manager)
    print("Direction : ", dir)
    while True:
        arduino.flushInput()                # Flushes Arduino's Input since it's not necessary anymore
        camera_manager.capture_image()
        camera_manager.transform_image()
        cv2.imshow("Cropped", camera_manager.cropped_image)
        cv2.imshow("New Image", camera_manager.polygon_image)
        if arduino.out_waiting == 0:
            angle = ImageAlgorithms.calculate_angle(camera_manager.polygon_image)
            command = f"{angle},{speed}.".encode()
            arduino.write(command)
            arduino.flush()
            # print(f"Sent command: {command.decode().strip()}")

        else:
            print("Arduino is busy, skipping command.")
        time.sleep(0.01)
        key = cv2.waitKey(1)  # Let OpenCV update the window
        if key == 27:  # Escape key to quit
            if (speed != 0):
                speed = 0
            else:
                break
        i = i+1
        print("index : ", i)
    cv2.destroyAllWindows()
    arduino.write(b'88,0.')