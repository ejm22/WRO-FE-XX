# A simple logger class that writes logs to a file with timestamps.
# It also prints the logs to the console.

import datetime
import os

LOG_DIR = "/WRO-FE-XX/pi/logs"

class Logger:
    def __init__(self):
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%M.%S")
        self.log_filename = f"log_{self.timestamp}.txt"
        self.current_log_path = os.path.join(LOG_DIR, self.log_filename)

    def log(self, msg):
        with open(self.current_log_path, "a") as f:
            f.write(f"[{datetime.datetime.now().isoformat()}] {msg}\n")
            print(f"[{datetime.datetime.now().isoformat()}] {msg}")
