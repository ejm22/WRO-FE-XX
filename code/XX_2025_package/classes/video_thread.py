from threading import Thread, Lock
import cv2
from queue import Queue
from classes.camera_manager import CameraManager
from classes.context_manager import ContextManager, RunStates
from classes.info_overlay_processor import InfoOverlayProcessor
import time
import numpy as np


class VideoThread(Thread):
    def __init__(self, camera_manager: CameraManager, context_manager: ContextManager, info_overlay_processor: InfoOverlayProcessor):
        Thread.__init__(self)
        self.camera_manager = camera_manager
        self.context_manager = context_manager
        self.info_overlay_processor = info_overlay_processor
        self.last_frame = None
        self.running = True
        self.daemon = True
        self.lock = Lock()
        self.queue = Queue()

    def run(self):
        while self.running:
            if self.context_manager.get_state() == RunStates.CHALLENGE_2_PARKING:
                with self.lock:
                    print('taking images from thread')
                    time.sleep(0.1)
                    self.camera_manager.capture_image()
                    self.camera_manager.transform_image()

                    with self.lock:
                        display_copy = self.camera_manager.display_image.copy()
                    
                    if not np.array_equal(self.last_frame, display_copy):
                        overlay_display = display_copy.copy()
                        self.info_overlay_processor.add_info_overlay(overlay_display)
                        self.camera_manager.add_frame_to_video(overlay_display)
                        self.last_frame = display_copy
                    
            if self.queue.get_nowait() == 'ADD_IMG':
                with self.lock:
                    display_copy = self.camera_manager.display_image.copy()
                    
                if not np.array_equal(self.last_frame, display_copy):
                    overlay_display = display_copy.copy()
                    self.info_overlay_processor.add_info_overlay(overlay_display)
                    self.camera_manager.add_frame_to_video(overlay_display)
                    self.last_frame = display_copy

    def stop(self):
        self.running = False
        cv2.destroyAllWindows()