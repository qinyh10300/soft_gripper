import cv2
import numpy as np
import multiprocessing
import threading
from gripper import gripper
from gripper_process import GripperProcess
from keystroke_counter import KeystrokeCounter, KeyCode
from utils import detect_yellow_block, detect_aruco
from audio import play_sound

def process_camera(camera_id, return_dict, index, stop_event):
    cap = cv2.VideoCapture(camera_id)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print(f"Error: Camera {camera_id} could not be opened.")
        return

    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            print(f"Error: Frame could not be captured from camera {camera_id}.")
            break

        center_yellow, w, h, mask_yellow = detect_yellow_block(frame)
        frame, center_aruco = detect_aruco(frame)

        if center_yellow is not None and center_aruco is not None:
            # 计算黄色色块中心和 ArUco 码中心的像素坐标差值
            delta_x = center_aruco[0] - center_yellow[0]
            delta_y = center_aruco[1] - center_yellow[1]
            print(f"Camera {camera_id} - ArUco Center: {center_aruco}, Yellow Block Center: {center_yellow}")
            print(f"Camera {camera_id} - Delta X: {delta_x}, Delta Y: {delta_y}")
        else:
            delta_x = -1000000
            delta_y = -1000000
            print(f"Camera {camera_id} - Either ArUco or Yellow Block was not detected.")

        # 缩小frame和mask_yellow到原来的80%
        frame_resized = cv2.resize(frame, (int(frame.shape[1] * 0.8), int(frame.shape[0] * 0.8)))
        mask_yellow_resized = cv2.resize(mask_yellow, (int(mask_yellow.shape[1] * 0.8), int(mask_yellow.shape[0] * 0.8)))

        return_dict[index] = (frame_resized, mask_yellow_resized, delta_x, delta_y)

    cap.release()

def async_play_sound(sound):
    """ 非阻塞方式播放声音 """
    play_sound(sound)

def main():
    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    stop_event = multiprocessing.Event()

    p1 = multiprocessing.Process(target=process_camera, args=(3, return_dict, 0, stop_event))  # 摄像头 3
    p2 = multiprocessing.Process(target=process_camera, args=(5, return_dict, 1, stop_event))  # 摄像头 5

    p1.start()
    p2.start()

    # with KeystrokeCounter() as key_counter:
    with KeystrokeCounter() as key_counter, \
        GripperProcess("/dev/ttyUSB0") as soft_gripper:
        flag = 0
        threshold = 20
        while True:
            if len(return_dict) == 2:  # 等待两个摄像头的结果
                frame1, mask1, delta_x_1, delta_y_1 = return_dict[0]
                frame2, mask2, delta_x_2, delta_y_2 = return_dict[1]

                combined_frame = np.hstack((frame1, frame2))
                combined_mask = np.hstack((mask1, mask2))
                combined_mask = cv2.cvtColor(combined_mask, cv2.COLOR_GRAY2BGR)

                final_combined = np.vstack((combined_frame, combined_mask))

                cv2.putText(final_combined, f"Camera 0 Delta X: {delta_x_1}, Delta Y: {delta_y_1}",
                                (100, 420), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(final_combined, f"Camera 1 Delta X: {delta_x_2}, Delta Y: {delta_y_2}",
                                (100, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                cv2.imshow('Final Combined Frame', final_combined)

                cv2.waitKey(1)

                if delta_x_2 == -1000000 or delta_x_2 == -1000000:
                    threading.Thread(target=async_play_sound, args=("未识别成功",)).start()
                    t = 0
                elif delta_x_1 > threshold:
                    threading.Thread(target=async_play_sound, args=("左",)).start()
                    t = 0
                elif delta_x_1 < -threshold:
                    threading.Thread(target=async_play_sound, args=("右",)).start()
                    t = 0
                elif delta_x_2 > threshold:
                    threading.Thread(target=async_play_sound, args=("后",)).start()
                    t = 0
                elif delta_x_2 < -threshold:
                    threading.Thread(target=async_play_sound, args=("前",)).start()
                    t = 0
                else:
                    threading.Thread(target=async_play_sound, args=("正确位置",)).start()
                    t += 1
                    if t > 20:
                        threading.Thread(target=async_play_sound, args=("正在抓取",)).start()
                        soft_gripper.catch()

            press_events = key_counter.get_press_events()
            for key_stroke in press_events:
                if key_stroke == KeyCode(char='q'): 
                    flag = -1
                    stop_event.set()  # 设置停止事件，通知子进程退出
                elif key_stroke == KeyCode(char='r'):
                     soft_gripper.release()
            if flag == -1:
                break

    p1.join()
    p2.join()

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
