from XX_2025_package.utils.enums import Direction


class ContextManager:
    CHALLENGE = 3

    def __init__(self):
        self._direction = Direction.LEFT
        self._lap_count = 0
        self._quarter_lap_count = 0
        self._start_position = None
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
    
    def set_start_position(self, start_position):
        self._start_position = start_position
    
    def has_completed_laps(self):
        return self._lap_count >= 3
    
    def get_start_position(self):
        return self._start_position