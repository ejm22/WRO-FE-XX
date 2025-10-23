from threading import Thread, Lock
import cv2
from classes.camera_manager import CameraManager
from classes.context_manager import ContextManager, RunStates
from classes.info_overlay_processor import InfoOverlayProcessor

class VideoThread(Thread):
    def __init__(self, camera_manager: CameraManager, context_manager: ContextManager, info_overlay_processor: InfoOverlayProcessor):
        Thread.__init__(self)
        self.camera_manager = camera_manager
        self.context_manager = context_manager
        self.info_overlay_processor = info_overlay_processor
        self.running = True
        self.daemon = True
        self.lock = Lock()

    def run(self):
        while self.running:
            if self.context_manager.get_state() == RunStates.CHALLENGE_2_PARKING:
                with self.lock:
                    self.camera_manager.capture_image()
                    self.camera_manager.transform_image()
                    
            if self.camera_manager.display_image is not None:
                with self.lock:
                    display_copy = self.camera_manager.display_image.copy()
                    
                self.info_overlay_processor.add_info_overlay()
                self.camera_manager.add_frame_to_video(display_copy)
                
                cv2.imshow("Display", display_copy)
                
                if cv2.waitKey(1) == 27:  # ESC key
                    self.running = False
                    break

    def stop(self):
        self.running = False
        cv2.destroyAllWindows()