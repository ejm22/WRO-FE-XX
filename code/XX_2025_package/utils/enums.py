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
    
