import cv2
import numpy as np

def detect_yellow_block(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_yellow = (20, 100, 100)
    upper_yellow = (30, 255, 255)
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    kernel = np.ones((5, 5), np.uint8)
    mask_yellow = cv2.erode(mask_yellow, kernel, iterations=1)
    mask_yellow = cv2.dilate(mask_yellow, kernel, iterations=1)
    contours_yellow, _ = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours_yellow) > 0:
        all_contours = np.concatenate(contours_yellow)
        x, y, w, h = cv2.boundingRect(all_contours)
        center = (x + w // 2, y + h // 2)
        
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)  # 黄色矩形框
        cv2.circle(frame, center, 5, (0, 0, 255), -1)  # 红色圆点表示中心
        
        return center, w, h, mask_yellow
    return None, None, None, mask_yellow

def detect_aruco(frame):
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()

    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=parameters)

    aruco_center = None
    if ids is not None:
        max_area = 0
        max_area_index = -1

        for i, id in enumerate(ids):
            if id == 13: 
                # 计算当前 ArUco 码的四个角点的面积
                contour = corners[i][0]
                area = cv2.contourArea(contour)

                if area > max_area:
                    max_area = area
                    max_area_index = i

        # 如果找到了面积最大的标记
        if max_area_index != -1:
            corners_of_max_area = corners[max_area_index][0]
            cX = int(np.mean(corners_of_max_area[:, 0]))  # 计算中心坐标
            cY = int(np.mean(corners_of_max_area[:, 1]))
            aruco_center = (cX, cY)
            cv2.circle(frame, (cX, cY), 5, (255, 0, 0), -1)  # 蓝色圆点表示ArUco标记中心
            print(f"ArUco Marker ID 13 center: ({cX}, {cY})")

    return frame, aruco_center