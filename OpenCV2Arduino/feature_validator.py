# feature_validator.py
import numpy as np
import cv2

def validate_shape(cnt, approx, shape_name):
    area = cv2.contourArea(cnt)
    if area < 1000:
        return False

    x, y, w, h = cv2.boundingRect(approx)
    aspect_ratio = w / h if h != 0 else 0

    if shape_name == "Square":
        # 要接近正方形，長寬比應接近1
        if aspect_ratio < 0.8 or aspect_ratio > 1.2:
            return False

    elif shape_name == "Triangle":
        # 三個頂點 + 面積篩選
        if len(approx) != 3:
            return False
        if area < 1500:
            return False

    elif shape_name == "Hexagon":
        # 近似六邊形頂點數為 6，允許誤差 ±1
        if len(approx) < 5 or len(approx) > 7:
            return False
        if area < 1500:
            return False

    return True
