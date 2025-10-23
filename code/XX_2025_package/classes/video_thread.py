from threading import Thread, Lock
import cv2
from queue import Queue, Empty
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
        try:
            while self.running:
                current_state = self.context_manager.get_state()
                
                if current_state == RunStates.CHALLENGE_2_PARKING:
                    with self.lock:
                        print('VideoThread: Capturing during parking')
                        self.camera_manager.capture_image()
                        self.camera_manager.transform_image()
                        display_copy = self.camera_manager.display_image.copy()
                    
                    overlay_display = display_copy.copy()
                    self.info_overlay_processor.add_info_overlay(overlay_display)
                    self.camera_manager.add_frame_to_video(overlay_display)
                    self.last_frame = display_copy
                    
                    time.sleep(0.05)
                    
                else:
                    try:
                        msg = self.queue.get(timeout=0.01)
                        if msg == 'ADD_IMG':
                            with self.lock:
                                if self.camera_manager.display_image is not None:
                                    display_copy = self.camera_manager.display_image.copy()
                                else:
                                    continue
                            
                            if self.last_frame is None or not np.array_equal(self.last_frame, display_copy):
                                overlay_display = display_copy.copy()
                                self.info_overlay_processor.add_info_overlay(overlay_display)
                                self.camera_manager.add_frame_to_video(overlay_display)
                                self.last_frame = display_copy
                                
                    except Empty:
                        time.sleep(0.001)
                        
        except Exception as e:
            print(f"VideoThread: Exception - {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("VideoThread: Stopped")

    def stop(self):
        print("VideoThread: Stop called")
        self.running = False