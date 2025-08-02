import cv2
import numpy as np
from classes.camera_manager import CameraManager

class HSVRangeHighlighter:
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

# 📷 Example usage
if __name__ == "__main__":

    camera_manager = CameraManager()
    camera_manager.start_camera()
    camera_manager.capture_image()
    img, colormask_img = camera_manager.transform_image()

    #image = cv2.imread("img/Image_1.jpg")
    #if image is None:
    #    raise ValueError("Image not found. Check the path.")

    hsv = cv2.cvtColor(camera_manager.current_image, cv2.COLOR_BGR2HSV)
    highlighter = HSVRangeHighlighter()
    highlighter.adjust_hsv(hsv, camera_manager.current_image)
