# confidence_scorer.py
import numpy as np
import cv2

def compute_confidence(cnt, approx, hsv_mask, shape):
    area = cv2.contourArea(cnt)
    if area < 1000:
        return 0.0

    x, y, w, h = cv2.boundingRect(approx)
    aspect_ratio = w / h if h != 0 else 0

        # ---------- 形狀得分計算 ----------
    if shape == "Square":
        shape_score = max(0.0, 1 - abs(1 - aspect_ratio))  # 越接近 1 越高

    elif shape == "Triangle":
        shape_score = 1.0 if len(approx) == 3 else 0.5

    elif shape == "Hexagon":
        # 接近6邊且平均邊長差異不大
        shape_score = 1.0 if 5 <= len(approx) <= 7 else 0.5
            
    else:
        shape_score = 0.3  # 其他未定義形狀的保底分

    # ---------- 遮罩密度得分 ----------
    mask_crop = hsv_mask[y:y+h, x:x+w]
    mask_area = cv2.countNonZero(mask_crop)
    density_score = mask_area / (w * h + 1)

    # ---------- 總分（可調整權重） ----------
    total_score = 0.6 * shape_score + 0.4 * density_score
    return total_score
