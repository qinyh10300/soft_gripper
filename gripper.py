import serial
from keystroke_counter import KeystrokeCounter, KeyCode

class gripper:
    def __init__(self, ser_name:str, baudrate=9600, timeout=1):
        self.ser = serial.Serial(port=ser_name, baudrate=baudrate, timeout=timeout)
        if self.ser.isOpen():
            print("Serial port is open.")
        else:
            print("Error: Serial port is not open.")
            self.ser.open()

    def catch(self):
        self.ser.write(b'\x00') 
        print("低电平")

    def release(self):
        self.ser.write(b'\xff') 
        print("高电平")

if __name__ == "__main__":
    with KeystrokeCounter() as key_counter, \
        gripper("/dev/ttyUSB0") as soft_gripper:
        flag = 0
        while True:
            press_events = key_counter.get_press_events()
            for key_stroke in press_events:
                if key_stroke == KeyCode(char='c'):
                    flag = 1
                elif key_stroke == KeyCode(char='r'):
                    flag = 0
                elif key_stroke == KeyCode(char='q'): 
                    flag = -1
            if flag == -1:
                break
            elif flag == 0:
                soft_gripper.release()
            else:
                soft_gripper.catch()