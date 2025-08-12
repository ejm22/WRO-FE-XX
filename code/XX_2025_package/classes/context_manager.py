

from enum import Enum
from XX_2025_package.utils.enums import Direction

class ContextManager:
    def __init__(self):
        self._direction = None
        self._lap_count = 0
        self._quarter_lap_count = 0
        # add more later
        
    def set_direction(self, direction: Direction):
        self.direction = direction
    
    def increment_lap_count(self):
        self.lap_count += 1
        
    def increment_quarter_lap_count(self):
        self.quarter_lap_count += 1
        
    def get_direction(self) -> Direction:
        return self._direction
    
    def get_lap_count(self):
        return self._lap_count
    
    def get_quarter_lap_count(self):
        return self._quarter_lap_count