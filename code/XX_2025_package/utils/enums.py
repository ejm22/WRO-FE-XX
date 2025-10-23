from enum import Enum

class Direction(Enum):
    LEFT = -1
    RIGHT = 1
    
class Color(Enum):
    BLUE = "blue"
    ORANGE = "orange"
    PINK = "pink"
    ALL_COLORS = "all_colors"
    RED = "red"
    GREEN = "green"
    WHITE = "white"
    
class StartPosition(Enum):
    BACK = "back"
    FRONT = "front"
    
class RunStates(Enum):
    INITIALIZATIONS = 0
    WAIT_FOR_START = 1
    CHALLENGE_1_FIND_DIRECTION = 11
    CHALLENGE_1_LAPS = 12
    CHALLENGE_1_PARKING = 13
    CHALLENGE_2_FIND_DIRECTION = 21
    CHALLENGE_2_LAPS = 22
    CHALLENGE_2_APPROACH = 23
    CHALLENGE_2_FORWARD = 24
    CHALLENGE_2_BACKWARDS = 25
    CHALLENGE_2_PARKING = 26
    STOP = 9
    
