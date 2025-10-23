import time

class DebugTimer:
    def __init__(self):
        self.start_time = None
        self.current_name = None

    def start(self, name: str):
        self.start_time = time.time()
        self.current_name = name

    def stop(self):
        print(f"Elapsed {self.current_name} time: {time.time() - self.start_time:.4f} seconds")