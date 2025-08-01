import cv2
import serial
import time
from classes.camera_manager import CameraManager
from utils.image_utils import ImageUtils
from classes.image_algoriths import ImageAlgorithms

arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)

if __name__ == "__main__":
    time.sleep(1)
    camera_manager = CameraManager()
    camera_manager.start_camera()
    cv2.namedWindow("White Zone", cv2.WINDOW_AUTOSIZE)
    arduino.write(b'v')
    time.sleep(0.1)
    line=arduino.readline().decode().strip()
    if line:
        print(line)
    while True:
        line = arduino.readline()
        camera_manager.capture_image()
        img = camera_manager.transform_image()
        contour_img = ImageUtils.draw_polygon(img, camera_manager.colormask_image.copy())
        cv2.imshow("Polygon Image", contour_img)
        #cv2.imshow("White Img", img)

        if arduino.out_waiting == 0:
            command = f"{ImageAlgorithms.calculate_angle(img)},4000.".encode()
            arduino.write(command)
            arduino.flush()
            # print(f"Sent command: {command.decode().strip()}")

        else:
            print("Arduino is busy, skipping command.")
        #arduino.write(f"{ImageUtils.find_angle_from_img(img)},3000.".encode())
        del img  # Free memory
        time.sleep(0.01)
        key = cv2.waitKey(1)  # Let OpenCV update the window
        if key == 27:  # Escape key to quit
            break
    cv2.destroyAllWindows()
    arduino.write(b'88,0.')