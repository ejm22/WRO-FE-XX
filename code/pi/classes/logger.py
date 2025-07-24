# A simple logger class that writes logs to a file with timestamps.
# It also prints the logs to the console.

import datetime
import os

LOG_DIR = "/WRO-FE-XX/pi/logs"
PTR_FILE = "/WRO-FE-XX/pi/config/log_ptr.txt"

timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%M.%S")
log_filename = f"log_{timestamp}.txt"
current_log_path = os.path.join(LOG_DIR, log_filename)

# Using a ptr file to know what current file is being used, while not overriding the others
with open(PTR_FILE, "w") as f:
    f.write(log_filename)
    
def log(msg):
    with open(current_log_path, "a") as f:
        f.write(f"[{datetime.datetime.now().isoformat()}] {msg}\n")
        # Also print to console
        print(f"[{datetime.datetime.now().isoformat()}] {msg}")