import cv2
import serial
import time
from XX_2025_package.classes.camera_manager import CameraManager
from XX_2025_package.utils.image_utils import ImageUtils
from XX_2025_package.classes.image_algoriths import ImageAlgorithms

arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)
speed = 5500
defi = 1

if __name__ == "__main__":
    ## 0 ##
    # Initialize program, camera, etc

    time.sleep(1)
    camera_manager = CameraManager()
    camera_manager.start_camera()
    arduino.write(b'v')
    time.sleep(0.1)
    line=arduino.readline().decode().strip()
    if line:
        print(line)
    i=0
    camera_manager.capture_image()
    camera_manager.transform_image()
    
    if (defi == 1):
        ## 1 ##
        # Find direction with blue and orange lines

        dir = ImageAlgorithms.get_direction(camera_manager)
        print("Direction : ", dir)

        ## 2 ##
        # Find starting area

        ## 2.1 ##
        # Adjust robot if starting area is problematic

        ## 3 ##
        # Complete 3 laps
        while True:
            arduino.flushInput()
            camera_manager.capture_image()
            camera_manager.transform_image()
            cv2.imshow("Cropped", camera_manager.cropped_image)
            cv2.imshow("New Image", camera_manager.polygon_image)
            if arduino.out_waiting == 0:
                angle = ImageAlgorithms.calculate_angle(camera_manager.polygon_image)
                command = f"{angle},{speed}.".encode()
                arduino.write(command)
                arduino.flush()
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

        ## 4 ##
        # Stop the robot in the correct zone

    if (defi == 2):
        ## 1 ##
        # Find direction with parking

        ## 2 ##
        # Analyze starting area (optional)

        ## 3 ##
        # Complete 3 laps
        while True:
            print("2")
        
        ## 4 ##
        # Approach the parking area

        ## 5 ##
        # Parallel park in the parking area
        
    cv2.destroyAllWindows()
    arduino.write(b'88,0.')