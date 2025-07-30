import serial
import time
import numpy as np
import cv2
from picamera2 import Picamera2

picam2 = Picamera2()

sensor_mode = picam2.sensor_modes[1]
sensor_width,sensor_height = sensor_mode["size"]

pic_width = 640
pic_height = 360

def find_black_from_bottom(img,col_range):
    y_vals = []
    for x in col_range:
        for y in reversed(range(pic_height)):
            if img[y,x] == 0:
                y_vals.append(y)
                break
        else:
            y_vals.append(0)
    return y_vals

config = (picam2.create_still_configuration(
    raw={"size":(sensor_width,sensor_height)},
    main={"format":'RGB888',"size": (pic_width,pic_height)}))
picam2.configure(config)
picam2.start()
time.sleep(2)

arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

time.sleep(2)

while True:
    img = picam2.capture_array()

    cropped_img = img[0:360,0:640]
    hsv = cv2.cvtColor(cropped_img,cv2.COLOR_BGR2HSV)

    # Define HSV range for blue (you can tune these)
    lower_blue = np.array([100, 100, 50])   # lower hue for blue
    upper_blue = np.array([130, 255, 255])  # upper hue for blue

    # Create a mask for blue
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Remove blue -> turn it to white
    cropped_img[blue_mask > 0] = (255,255,255) 
    img2gray = cv2.cvtColor(cropped_img,cv2.COLOR_BGR2GRAY)
    blurred_img = cv2.bilateralFilter(img2gray,9,75,75)
    _, binary_img = cv2.threshold(blurred_img, 100, 255, cv2.THRESH_BINARY)  # Invert threshold
    kernel = np.ones((5, 5), np.uint8)
    cleaned_binary = cv2.morphologyEx(binary_img, cv2.MORPH_CLOSE, kernel)

    # Find contours
    contours, _ = cv2.findContours(cleaned_binary,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    # Assume the largest white region is the surface
    white_zone_contour = max(contours, key=cv2.contourArea)

    # Visualize the detected white zone
    visualized = cv2.cvtColor(cleaned_binary, cv2.COLOR_GRAY2BGR)  # Convert to color for drawing
    cv2.drawContours(visualized, [white_zone_contour], -1, (0, 255, 0), 2)  # Green contour, thickness 2
    cv2.imshow("White Zone", visualized)

    # Analyse first and last 10 colums
    nbr_cols = 10
    left_cols = range(0,nbr_cols)
    right_cols = range(pic_width - nbr_cols, pic_width)

    left_y_vals = find_black_from_bottom(cleaned_binary,left_cols)
    right_y_vals = find_black_from_bottom(cleaned_binary,right_cols)

    avg_left_y = np.mean(left_y_vals)
    avg_right_y = np.mean(right_y_vals)

    angle = 88 + (int((avg_left_y-avg_right_y) / 10))   
    message = f"{angle},3000."
    arduino.write(b'message')
    time.sleep(0.1)
