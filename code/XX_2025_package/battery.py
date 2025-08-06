import serial
import time

arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)

if __name__ == "__main__":
    time.sleep(2)
    arduino.write(b'v')
    time.sleep(0.1)
    line=arduino.readline().decode().strip()
    if line:
        print(line)