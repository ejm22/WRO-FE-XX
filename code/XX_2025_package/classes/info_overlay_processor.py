from classes.context_manager import ContextManager
from classes.camera_manager import CameraManager
from utils.image_drawing_utils import ImageDrawingUtils

class InfoOverlayProcessor:
    def __init__(self, context_manager: ContextManager, camera_manager: CameraManager):
        self.context_manager = context_manager
        self.camera_manager = camera_manager
        
    def get_display_image(self):
        return self.camera_manager.display_image
    
    def add_info_overlay(self, frame=None):
        if frame is None:
            frame = self.camera_manager.display_image
        self.add_lap_info(frame)
        self.add_state_info(frame)
        self.add_timer_info(frame)
        self.add_speed_info(frame)
    
    def add_lap_info(self, frame):
        if frame is not None:
            lap_count = self.context_manager.get_lap_count()
            quarter_lap_count = self.context_manager.get_quarter_lap_count()
            ImageDrawingUtils.add_text_to_image(frame, f"Lap: {lap_count} {f'{quarter_lap_count}/4' if quarter_lap_count != 0 else ''}", (10, 60), (0, 0, 255))

    def add_state_info(self, frame):
        if frame is not None:
            self.context_manager.get_state()
            ImageDrawingUtils.add_text_to_image(frame, f"State: {self.context_manager.get_state().name}", (10, 30), (0, 255, 0))
            
    def add_timer_info(self, frame):
        if frame is not None:
            elapsed = self.context_manager.get_elapsed_time()
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            timer_text = f"{minutes:02d}:{seconds:02d}"
            ImageDrawingUtils.add_text_to_image(frame, f"Time: {timer_text}", (10, 90), (255, 0, 0))

    def add_speed_info(self,frame):
        if frame is not None:
            speed_state = self.context_manager.get_speed_state()
            ImageDrawingUtils.add_text_to_image(frame, f"Speed: {speed_state.name}", (10, 120), (0, 255, 0))  