import cv2
import numpy as np
from classes.camera_manager import CameraManager
import os

class HSVRangeHighlighter:
    def __init__(self, window_name="HSV Range Highlighter", max_width=800, max_height=600):
        self.window_name = window_name
        self.max_width = max_width
        self.max_height = max_height
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        self._create_hsv_trackbars()
        self.paused = False

    def _create_hsv_trackbars(self):
        cv2.createTrackbar("Hue Min", self.window_name, 0, 179, lambda x: None)
        cv2.createTrackbar("Hue Max", self.window_name, 179, 179, lambda x: None)
        cv2.createTrackbar("Sat Min", self.window_name, 0, 255, lambda x: None)
        cv2.createTrackbar("Sat Max", self.window_name, 255, 255, lambda x: None)
        cv2.createTrackbar("Val Min", self.window_name, 0, 255, lambda x: None)
        cv2.createTrackbar("Val Max", self.window_name, 255, 255, lambda x: None)

    def _apply_hsv_mask(self, bgr_image):
        hsv = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)
        h_min = cv2.getTrackbarPos("Hue Min", self.window_name)
        h_max = cv2.getTrackbarPos("Hue Max", self.window_name)
        s_min = cv2.getTrackbarPos("Sat Min", self.window_name)
        s_max = cv2.getTrackbarPos("Sat Max", self.window_name)
        v_min = cv2.getTrackbarPos("Val Min", self.window_name)
        v_max = cv2.getTrackbarPos("Val Max", self.window_name)
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])
        mask = cv2.inRange(hsv, lower, upper)
        red_overlay = np.zeros_like(bgr_image)
        red_overlay[:, :] = [0, 0, 255]
        highlighted = cv2.bitwise_and(red_overlay, red_overlay, mask=mask)
        return cv2.addWeighted(bgr_image, 0.5, highlighted, 0.5, 0)

    def adjust_hsv_image(self, bgr_image):
        while True:
            if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1:
                break
            result = self._apply_hsv_mask(bgr_image)
            cv2.imshow(self.window_name, result)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
        cv2.destroyAllWindows()

    def adjust_hsv_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Failed to open video: {video_path}")
            return

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        current_frame = 0

        def on_trackbar(pos):
            nonlocal current_frame
            current_frame = pos
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos)

        cv2.createTrackbar("Position", self.window_name, 0, total_frames - 1, on_trackbar)

        while True:
            if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1:
                break

            if not self.paused:
                ret, frame = cap.read()
                if not ret:
                    break
                current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                cv2.setTrackbarPos("Position", self.window_name, current_frame)

            if ret:
                frame_hsv = self._apply_hsv_mask(frame)
                cv2.imshow(self.window_name, frame_hsv)

            key = cv2.waitKey(30) & 0xFF
            if key == 27:  # ESC
                break
            elif key == ord(" "):  # Space = pause/play
                self.paused = not self.paused
                
            # Fonctionne pas.
            elif key == 81:  # Left arrow = step back one frame
                if self.paused:
                    current_frame = max(0, current_frame - 1)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
            elif key == 83:  # Right arrow = step forward one frame
                if self.paused:
                    current_frame = min(total_frames - 1, current_frame + 1)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    print("Choose input mode:")
    print("1 - Take new picture (Pi only)")
    print("2 - Load image from tests/images")
    print("3 - Load video from tests/videos")

    choice = input("Enter 1, 2, or 3: ").strip()
    highlighter = HSVRangeHighlighter(max_width=1200, max_height=800)

    if choice == "1":
        camera_manager = CameraManager()
        camera_manager.start_camera()
        camera_manager.capture_image()
        image = camera_manager.raw_image
        highlighter.adjust_hsv_image(image)

    elif choice == "2":
        bgr_image = cv2.imread("tests/images/img.png")
        if bgr_image is not None:
            highlighter.adjust_hsv_image(bgr_image)
        else:
            print(f"Failed to load image, check path")

    elif choice == "3":
        highlighter.adjust_hsv_video("tests/videos/video.mp4")

    else:
        print("Invalid choice. Exiting.")
