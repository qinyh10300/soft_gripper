import serial
import time

ser = serial.Serial(port="/dev/ttyUSB0", baudrate=9600, timeout=1)

if ser.isOpen():
    print("Serial port is open.")
else:
    print("Error: Serial port is not open.")
    ser.open()

while True:
    ser.write(b'\x00') 
    print("低电平")
# time.sleep(1) 

# ser.close()