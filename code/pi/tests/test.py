import serial
import time

arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)

def control_led(state):
    if state == 'on':
        arduino.write(b'1')
        print("LED ON")
    elif state == 'off':
        arduino.write(b'0')
        print("LED OFF")

while True:
    control_led('on')
    time.sleep(1)
    control_led('off')
    time.sleep(1)