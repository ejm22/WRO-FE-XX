from enum import Enum
from XX_2025_package.utils.enums import Direction


class ContextManager:
    challenge = 1

    def __init__(self):
        self._direction = None
        self._lap_count = 0
        self._quarter_lap_count = 0
        # add more later
        
    def set_direction(self, direction: Direction):
        self._direction = direction
        
    def increment_quarter_lap_count(self):
        self._quarter_lap_count += 1
        print(f"{self._quarter_lap_count} /4 of lap")
        if (self._quarter_lap_count >= 4):
            self._lap_count += 1
            self._quarter_lap_count = 0
            print(f"Lap completed! Total laps: {self._lap_count}")
        
    def get_direction(self) -> Direction:
        return self._direction
    
    def get_lap_count(self):
        return self._lap_count
    
    def get_quarter_lap_count(self):
        return self._quarter_lap_count
    
    def has_completed_laps(self):
        return self._lap_count >= 3