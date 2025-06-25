# main.py
import cv2
import numpy as np
from OpenCV2Arduino import SignalSender, StateManager, AppUI

# ====== 主要參數設定 ======
COM_PORT = 'COM4'        # <<< 這裡填寫你的 Arduino COM port
BAUD_RATE = 9600         # <<< 這裡填寫你的 Serial Baudrate
# ====== 攝影機設定 ======
cap1 = cv2.VideoCapture(0)  # <<< 依實際情況修改（0 通常是內建攝影機，1 是外接攝影機）

# 顏色+形狀對應 Arduino 指令代碼（可依需求修改下方對應表）
action_map = {
    ('Red', 'Triangle'): 'A',
    ('Red', 'Square'): 'B',
    ('Red', 'Hexagon'): 'C',
    ('Blue', 'Triangle'): 'D',
    ('Blue', 'Square'): 'E',
    ('Blue', 'Hexagon'): 'F',
}

# 在這裡設定 HSV 範圍與最小面積
color_ranges = {
    "Red": {
        "lower": [161, 186, 189],
        "upper": [179, 255, 255],
        "min_area": 1500
    },
    "Blue": {
        "lower": [98, 255, 139],
        "upper": [116, 255, 221],
        "min_area": 1500
    }
}

# ====== 目標偵測主函式 ======
def detect_target(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # 轉 HSV
    result_frame = frame.copy()
    mask_total = np.zeros(hsv.shape[:2], dtype=np.uint8)  # 全部遮罩
    detected_labels = []

    for color_name, cfg in color_ranges.items():
        lower_np = np.array(cfg["lower"])
        upper_np = np.array(cfg["upper"])
        min_area = cfg.get("min_area", 1000)
        mask = cv2.inRange(hsv, lower_np, upper_np)  # 產生遮罩
        mask_total = cv2.bitwise_or(mask_total, mask)
        cv2.imshow(f"{color_name} Mask", mask)  # 顯示遮罩

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)  # 多邊形近似
            x, y, w, h = cv2.boundingRect(approx)
            num_vertices = len(approx)
            area = cv2.contourArea(cnt)
            aspect_ratio = w / h if h != 0 else 0

            shape = None
            if num_vertices == 3 and area >= min_area:
                shape = "Triangle"
            elif num_vertices == 4 and 0.8 < aspect_ratio < 1.2 and area >= min_area:
                shape = "Square"
            elif 6 <= num_vertices <= 7 and area >= min_area:
                shape = "Hexagon"

            if shape:
                label = action_map.get((color_name, shape), None)
                if label:
                    detected_labels.append(label)
                    cv2.drawContours(result_frame, [approx], -1, (0, 255, 0), 2)
                    cv2.putText(result_frame,
                        f"{color_name}-{shape} :{int(area)}",
                        (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (255, 255, 255), 2)
    return result_frame, detected_labels, mask_total

# ====== 主程式 ======
def main():
    cap = cap1  # 使用攝影機
    sender = SignalSender(port=COM_PORT, baudrate=BAUD_RATE)  # 建立 Serial 傳送物件
    ui = AppUI()  # 建立 UI 物件

    if not cap.isOpened():
        print("[Main] Camera not accessible.")
        return

    print("[Main] System running. Press 'q' to quit.")
    state_manager = StateManager()  # 狀態管理（多幀穩定判斷）

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        result_frame, labels, mask = detect_target(frame)  # 目標偵測
        ui.update(frame, result_frame, mask, labels)       # 更新畫面

        if labels:
            state_manager.update(labels[0])  # 有偵測到目標，更新狀態
        else:
            stable_label = state_manager.update(None)  # 沒有偵測到，檢查是否有穩定結果
            if stable_label:
                print(f"[Main] 穩定觸發：{stable_label}")
                sender.send_async(stable_label)  # 非同步傳送訊號給 Arduino

        if ui.should_quit():
            break

    cap.release()
    cv2.destroyAllWindows()
    sender.close()
    print("[Main] System exited.")

if __name__ == '__main__':
    main()