import serial
import time

arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

time.sleep(2)

def control_led(state):
    if state == 'on':
        arduino.write(b'1')
        print("LED ON")
    elif state == 'off':
        arduino.write(b'0')
        print("LED OFF")

while True:
    arduino.write(b'v')
    time.sleep(1)
    line=arduino.readline().decode().strip()
    if line:
        print(line)
    arduino.write(b'88,4000.')
    time.sleep(1.5)    
    arduino.write(b'88,0.')
    time.sleep(1.5)    
    arduino.write(b'88,-4000.')
    time.sleep(1.5)    
    #arduino.write(b'110,1000.')
    #time.sleep(1)    
    #arduino.write(b'100,2000.')
    #time.sleep(1)    
    #arduino.write(b'80,-1000.')
    #time.sleep(1)    
    arduino.write(b'88,0.')
    time.sleep(1)
