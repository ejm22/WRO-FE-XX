from enum import Enum
import numpy as np
from XX_2025_package.utils.enums import Direction
from XX_2025_package.utils.image_color_utils import ImageColorUtils
from XX_2025_package.utils.image_transform_utils import ImageTransformUtils
from XX_2025_package.utils.enums import Color
import time

class LapState(Enum):
    INITIAL_STATE = 0
    WAITING_STATE = 1
    LOOKING_FOR_BLUE = 2
    LOOKING_FOR_ORANGE = 3
    
class LapTracker:
    def __init__(self, context_manager):
        self._state = LapState.INITIAL_STATE
        self.context_manager = context_manager
        self.time_stamp = 0

    def process_image(self, blue_img, orange_img):
        """
        Process the given blue and orange mask images to track lap progress, using a state machine.
        I/O:
            blue_img: binary image mask for blue color
            orange_img: binary image mask for orange color
        """
        if self.context_manager.get_direction() is not None:
            finds_blue = np.any(blue_img[ImageTransformUtils.PIC_HEIGHT - 130: ImageTransformUtils.PIC_HEIGHT - 30, ImageTransformUtils.PIC_WIDTH // 2 - 20: ImageTransformUtils.PIC_WIDTH // 2 + 20])
            finds_orange = np.any(orange_img[ImageTransformUtils.PIC_HEIGHT - 130: ImageTransformUtils.PIC_HEIGHT - 30, ImageTransformUtils.PIC_WIDTH // 2 - 20: ImageTransformUtils.PIC_WIDTH // 2 + 20])
            if (self.context_manager.get_direction() == Direction.LEFT):
                if finds_blue:
                    self._process_color(Color.BLUE)
                elif finds_orange:
                    self._process_color(Color.ORANGE)
            else:
                if finds_orange:
                    self._process_color(Color.ORANGE)
                elif finds_blue:
                    self._process_color(Color.BLUE)



    def _process_color(self, detected_color):
        """
        Process the detected color based on the current direction and state.
        I/O:
            detected_color: Color enum indicating the detected color (BLUE or ORANGE)
        """
        direction = self.context_manager.get_direction()
        if direction == Direction.LEFT:
            self._process_left_direction(detected_color)
        elif direction == Direction.RIGHT:
            self._process_right_direction(detected_color)
            
    
    def _process_left_direction(self, detected_color):
        """
        Changes state depending on color detected.
        I/O:
            detected_color: Color enum indicating the detected color (BLUE or ORANGE)
        """
        if self._state == LapState.INITIAL_STATE:
            self._state = LapState.LOOKING_FOR_BLUE

        if self._state == LapState.WAITING_STATE:
            if self.time_stamp == 0:
                self.time_stamp = time.time()

            if time.time() - self.time_stamp >= 0.5:
                self._state = LapState.LOOKING_FOR_BLUE
                self.time_stamp = time.time()

        elif self._state == LapState.LOOKING_FOR_BLUE and detected_color == Color.BLUE:
            self._state = LapState.LOOKING_FOR_ORANGE

        elif self._state == LapState.LOOKING_FOR_ORANGE and detected_color == Color.ORANGE:

            self.context_manager.increment_quarter_lap_count()
            self._state = LapState.WAITING_STATE


            

    def _process_right_direction(self, detected_color):
        """
        Changes state depending on color detected.
        I/O:
            detected_color: Color enum indicating the detected color (BLUE or ORANGE)
        """
        if self._state == LapState.INITIAL_STATE:
            self._state = LapState.LOOKING_FOR_ORANGE
    
        if self._state == LapState.WAITING_STATE:
            if self.time_stamp == 0:
                self.time_stamp = time.time()

            if time.time() - self.time_stamp >= 0.5:
                self._state = LapState.LOOKING_FOR_ORANGE
                self.time_stamp = time.time()

        elif self._state == LapState.LOOKING_FOR_ORANGE and detected_color == Color.ORANGE:
            self._state = LapState.LOOKING_FOR_BLUE

        elif self._state == LapState.LOOKING_FOR_BLUE and detected_color == Color.BLUE:
            self.context_manager.increment_quarter_lap_count()
            self._state = LapState.WAITING_STATE

            