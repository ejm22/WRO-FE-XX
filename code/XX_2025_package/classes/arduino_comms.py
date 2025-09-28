import serial
import time

class ArduinoComms:
	def __init__(self, port='/dev/ttyACM0', baudrate=115200, timeout=0.1):
		self.arduino = serial.Serial(port, baudrate, timeout=timeout)

	def send(self, type, angle = 85, speed = 0, distance = 0):
		if type == '!':
			command = f"{angle}!".encode()
			self.arduino.write(command)
		elif type == 'm':
			command = f"m{angle},{speed}.".encode()
			self.arduino.write(command)
		elif type == 't':
			command = f"t{angle},{speed},{distance}.".encode()
			self.arduino.write(command)
			while (self.read() != 'F'):
				time.sleep(0.005)
		self.arduino.flush()

	def read(self, size=1):
		if self.arduino.in_waiting > 0:
			return self.arduino.read(size).decode('utf-8')
		return None