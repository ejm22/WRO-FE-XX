# We run this server to have access to the logs live from the Raspberry Pi ip, even when it isn't
# connected to a monitor, for debugging purposes.

from flask import Flask
import os

app = Flask(__name__)
LOG_DIR = "/WRO-FE-XX/pi/logs"
PTR_FILE = "/WRO-FE-XX/pi/config/log_ptr.txt"

# Creating a /logs route that fetches the current log file every two seconds
@app.route('/logs')
def live_logs():
    try:
        with open(PTR_FILE, "r") as ptr_f:
            current_filename = ptr_f.read().strip()
        
        log_path = os.path.join(LOG_DIR, current_filename)
        
        with open(log_path, "r") as log_f:
            logs = log_f.readlines()
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta http-equiv="refresh" content="2">
            <title>Live Logs</title>
        </head>
        <body>
            <h1>Live Logs from {current_filename}</h1>
            <pre>{''.join(logs)}</pre>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h1>Error fetching logs: {str(e)}</h1>"
    
# Run the flask app when the main runs. Could be changed later if we want to run it after the main ends.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

