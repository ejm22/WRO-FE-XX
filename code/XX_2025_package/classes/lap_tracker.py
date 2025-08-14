from enum import Enum
import numpy as np
from XX_2025_package.utils.enums import Direction
from XX_2025_package.utils.image_color_utils import ImageColorUtils
from XX_2025_package.utils.image_transform_utils import ImageTransformUtils
from XX_2025_package.utils.enums import Color
from XX_2025_package.classes.logger import Logger
import time

LINE_COORDS = {
    Direction.RIGHT: (ImageTransformUtils.PIC_HEIGHT - 1, 0),
    Direction.LEFT: (ImageTransformUtils.PIC_HEIGHT - 1, ImageTransformUtils.PIC_WIDTH - 1)
}

class LapState(Enum):
    INITIAL_STATE = 1
    LOOKING_FOR_BLUE = 2
    LOOKING_FOR_ORANGE = 3
    
class LapTracker:
    def __init__(self, context_manager):
        self._state = LapState.INITIAL_STATE
        self.lap_count = 0
        self.context_manager = context_manager

    def process_image(self, blue_img, orange_img):
        if self.context_manager.get_direction() is not None:
            finds_blue = np.any(blue_img[ImageTransformUtils.PIC_HEIGHT - 50: ImageTransformUtils.PIC_HEIGHT - 30, ImageTransformUtils.PIC_WIDTH // 2 - 20: ImageTransformUtils.PIC_WIDTH // 2 + 20])
            finds_orange = np.any(orange_img[ImageTransformUtils.PIC_HEIGHT - 50: ImageTransformUtils.PIC_HEIGHT - 30, ImageTransformUtils.PIC_WIDTH // 2 - 20: ImageTransformUtils.PIC_WIDTH // 2 + 20])
            if finds_blue:
                self._process_color(Color.BLUE)
            if finds_orange:
                self._process_color(Color.ORANGE)


    def _process_color(self, detected_color):
        direction = self.context_manager.get_direction()
        if direction == Direction.LEFT:
            self._process_left_direction(detected_color)
        elif direction == Direction.RIGHT:
            self._process_right_direction(detected_color)
            
    
    def _process_left_direction(self, detected_color):
        if self._state == LapState.INITIAL_STATE:
            self._state = LapState.LOOKING_FOR_BLUE

        elif self._state == LapState.LOOKING_FOR_BLUE and detected_color == Color.BLUE:
            self._state = LapState.LOOKING_FOR_BLUE
            time.sleep(0.1)
            self.context_manager.increment_quarter_lap_count()
            

    def _process_right_direction(self, detected_color):
        if self._state == LapState.INITIAL_STATE:
            self._state = LapState.LOOKING_FOR_ORANGE

        elif self._state == LapState.LOOKING_FOR_ORANGE and detected_color == Color.ORANGE:
            self._state = LapState.LOOKING_FOR_BLUE

        elif self._state == LapState.LOOKING_FOR_BLUE and detected_color == Color.BLUE:
            self._state = LapState.LOOKING_FOR_ORANGE
            time.sleep(0.1)
            self.context_manager.increment_quarter_lap_count()