import serial
import time

ser = serial.Serial(port="/dev/ttyUSB0", baudrate=9600, timeout=1)

if ser.isOpen():
    print("Serial port is open.")
else:
    print("Error: Serial port is not open.")
    ser.open()

while True:
    ser.write(b'\xff')  # 发送字符 '1' 表示高电平
    print("高电平")
time.sleep(1)  # 等待1秒

ser.close()