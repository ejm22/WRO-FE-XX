from enum import Enum
from XX_2025_package.utils.enums import Direction
from XX_2025_package.utils.image_color_utils import ImageColorUtils
from XX_2025_package.utils.image_transform_utils import ImageTransformUtils
from XX_2025_package.utils.enums import Color
from XX_2025_package.classes.logger import Logger
import time

LINE_COORDS = {
    Direction.LEFT: (ImageTransformUtils.PIC_HEIGHT - 1, 0),
    Direction.RIGHT: (ImageTransformUtils.PIC_HEIGHT - 1, ImageTransformUtils.PIC_WIDTH - 1)
}

class LapState(Enum):
    LOOKING_FOR_WHITE = 1
    LOOKING_FOR_BLUE = 2
    LOOKING_FOR_ORANGE = 3
    
class LapTracker:
    def __init__(self, context_manager):
        self._state = LapState.LOOKING_FOR_WHITE
        self.lap_count = 0
        self.context_manager = context_manager
        self.logger = Logger()

    def process_image(self, img):
        if self.context_manager.get_direction() is not None:
            self._process_color(ImageColorUtils.find_color_from_pt(img, LINE_COORDS[self.context_manager.get_direction()]))

    
    def _process_color(self, detected_color):
        direction = self.context_manager.get_direction()
        if direction == Direction.LEFT:
            self._process_left_direction(detected_color)
        elif direction == Direction.RIGHT:
            self._process_right_direction(detected_color)
            
    
    def _process_left_direction(self, detected_color):
        if self._state == LapState.LOOKING_FOR_WHITE and detected_color == Color.WHITE:
            # wait 0.5 before checking for next turn
            time.sleep(0.5)
            self._state = LapState.LOOKING_FOR_BLUE

        elif self._state == LapState.LOOKING_FOR_BLUE and detected_color == Color.BLUE:
            self._state = LapState.LOOKING_FOR_ORANGE

        elif self._state == LapState.LOOKING_FOR_ORANGE and detected_color == Color.ORANGE:
            self._state = LapState.LOOKING_FOR_WHITE
            self.context_manager.increment_quarter_lap_count()
            print("Quarter lap completed, returning to initial state.")
            

    def _process_right_direction(self, detected_color):
        if self._state == LapState.LOOKING_FOR_WHITE and detected_color == Color.WHITE:
            # wait 0.5 before checking for next turn
            time.sleep(0.5)
            self._state = LapState.LOOKING_FOR_ORANGE

        elif self._state == LapState.LOOKING_FOR_ORANGE and detected_color == Color.ORANGE:
            self._state = LapState.LOOKING_FOR_BLUE

        elif self._state == LapState.LOOKING_FOR_BLUE and detected_color == Color.BLUE:
            self._state = LapState.LOOKING_FOR_WHITE
            self.context_manager.increment_quarter_lap_count()
            print("Quarter lap completed, returning to initial state.")