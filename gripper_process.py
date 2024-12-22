import serial
import multiprocessing as mp
from keystroke_counter import KeystrokeCounter, KeyCode
import time

class GripperProcess(mp.Process):
    def __init__(self, ser_name: str, baudrate=9600, timeout=1):
        super().__init__()
        self.ser_name = ser_name
        self.baudrate = baudrate
        self.timeout = timeout
        self.running = mp.Event()  # 用于控制进程循环
        self.ser = serial.Serial(port=self.ser_name, baudrate=self.baudrate, timeout=self.timeout)

        if self.ser.isOpen():
            print("Serial port is open.")
        else:
            print("Error: Serial port is not open.")
            self.ser.open()

    def __enter__(self):
        self.start()
        return self 

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop() 
        self.ser.close()
        print("Serial port closed.")

    def run(self):
        while True:
            if self.running.is_set():
                self.ser.write(b'\x00') 
                self.ser.flush() 
                print("低电平")
                # time.sleep(0.1) 
            else:
                self.ser.write(b'\xff') 
                self.ser.flush() 
                print("高电平")
                # time.sleep(0.1) 

    def catch(self):
        self.running.set() 

    def release(self):
        self.running.clear() 

    def stop(self):
        self.running.clear()
        self.ser.close()
        self.terminate()  # 强制终止进程


if __name__ == "__main__":
    with KeystrokeCounter() as key_counter,\
        GripperProcess("/dev/ttyUSB0") as soft_gripper:
        
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
                soft_gripper.stop()
                break
            elif flag == 0:
                soft_gripper.release()  
            else:
                soft_gripper.catch()
