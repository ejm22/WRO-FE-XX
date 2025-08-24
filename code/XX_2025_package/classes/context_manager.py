from XX_2025_package.utils.enums import Direction
from XX_2025_package.utils.enums import StartPosition

class ContextManager:
    LAP_GOAL = 1
    CHALLENGE = None

    def __init__(self):
        self._direction = Direction.LEFT
        self._lap_count = 0
        self._quarter_lap_count = 0
        self._start_position = None
        self._parking_distance = 0
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
    
    def set_challenge(self, challenge):
        if (challenge != 1 and challenge != 2):
            print(f"Warning: Challenge must be 1 or 2, not {challenge}")
        ContextManager.CHALLENGE = challenge
    
    def get_parking_distance(self):
        offset = 0
        if self.get_start_position() == StartPosition.BACK:
            offset = 1 
        else: 
            offset = 3
        return self._parking_distance - offset
    
    def set_start_position(self, start_position):
        self._start_position = start_position

    def set_parking_distance(self, distance):
        print(f"Parking distance set to {distance}")
        self._parking_distance = distance
    
    def has_completed_laps(self):
        return self._lap_count >= self.LAP_GOAL
    
    def get_start_position(self):
        return self._start_position
    
    def is_last_quarter(self):
        return self._lap_count == self.LAP_GOAL - 1 and self._quarter_lap_count == 3