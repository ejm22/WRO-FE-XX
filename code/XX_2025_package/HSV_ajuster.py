import cv2
import numpy as np
from XX_2025_package.classes.camera_manager import CameraManager

class HSVRangeHighlighter:
    """
    A utility class to adjust and highlight specific HSV ranges in an image using OpenCV trackbars.
    """
    def __init__(self, window_name="HSV Range Highlighter"):
        self.window_name = window_name
        cv2.namedWindow(self.window_name)
        self._create_trackbars()

    def _create_trackbars(self):
        cv2.createTrackbar("Hue Min", self.window_name, 0, 179, lambda x: None)
        cv2.createTrackbar("Hue Max", self.window_name, 179, 179, lambda x: None)
        cv2.createTrackbar("Sat Min", self.window_name, 0, 255, lambda x: None)
        cv2.createTrackbar("Sat Max", self.window_name, 255, 255, lambda x: None)
        cv2.createTrackbar("Val Min", self.window_name, 0, 255, lambda x: None)
        cv2.createTrackbar("Val Max", self.window_name, 255, 255, lambda x: None)

    def adjust_hsv(self, hsv_image, original_bgr):
        while True:
            h_min = cv2.getTrackbarPos("Hue Min", self.window_name)
            h_max = cv2.getTrackbarPos("Hue Max", self.window_name)
            s_min = cv2.getTrackbarPos("Sat Min", self.window_name)
            s_max = cv2.getTrackbarPos("Sat Max", self.window_name)
            v_min = cv2.getTrackbarPos("Val Min", self.window_name)
            v_max = cv2.getTrackbarPos("Val Max", self.window_name)

            lower = np.array([h_min, s_min, v_min])
            upper = np.array([h_max, s_max, v_max])

            mask = cv2.inRange(hsv_image, lower, upper)

            red_overlay = np.zeros_like(original_bgr)
            red_overlay[:, :] = [0, 0, 255]  # Red in BGR

            highlighted = cv2.bitwise_and(red_overlay, red_overlay, mask=mask)
            result = cv2.addWeighted(original_bgr, 0.5, highlighted, 0.5, 0)

            cv2.imshow(self.window_name, result)

            if cv2.waitKey(1) & 0xFF == 27:
                break
            if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1:
                break

        cv2.destroyAllWindows()

if __name__ == "__main__":

    take_picture = bool(int(input("take new pic? 1 for yes, 0 for no: ")))
    camera_manager = CameraManager()
    if (take_picture):
        camera_manager.start_camera()
        camera_manager.capture_image() 
    else:
        bgr_image = cv2.imread("tests/images/img.png")
        if bgr_image is not None:
            camera_manager.raw_image = bgr_image
        else:
            print("Failed to load image.")
            exit(1)
    
    
    camera_manager.transform_image()

    hsv = cv2.cvtColor(camera_manager.raw_image, cv2.COLOR_BGR2HSV)
    highlighter = HSVRangeHighlighter()
    highlighter.adjust_hsv(hsv, camera_manager.raw_image)
