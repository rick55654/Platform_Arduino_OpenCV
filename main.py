# main.py
import cv2
import numpy as np
import json
from pathlib import Path
from OpenCV2Arduino import SignalSender, StateManager

# ====== 主要參數設定 ======
COM_PORT = 'COM7'        # <<< 這裡填寫你的 Arduino COM port
BAUD_RATE = 9600         # <<< 這裡填寫你的 Serial Baudrate

# --- config: color_ranges, action_map ---
color_config_path = Path(__file__).parent / "OpenCV2Arduino" / "color_config.json"
with open(color_config_path, "r", encoding="utf-8") as f:
    color_ranges = json.load(f)  # 讀取 HSV 顏色範圍設定

# 顏色+形狀對應 Arduino 指令代碼
action_map = {
    ('Red', 'Triangle'): 'A',
    ('Red', 'Square'): 'B',
    ('Red', 'Hexagon'): 'C',
    ('Blue', 'Triangle'): 'D',
    ('Blue', 'Square'): 'E',
    ('Blue', 'Hexagon'): 'F',
}

# ====== UI 類別整合（優化版）======
class AppUI:
    def __init__(self, window_name="ARMCtrl Demo"):  # <<< 這裡可自訂視窗名稱
        self.window_name = window_name
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        self.mask_windows = ["Red Mask", "Blue Mask"]  # 遮罩視窗名稱

    def update(self, original_frame, annotated_frame, mask_frame, label=None):
        # Resize 畫面
        left = cv2.resize(annotated_frame, (640, 480))
        right = cv2.cvtColor(cv2.resize(mask_frame, (640, 480)), cv2.COLOR_GRAY2BGR)

        # 顯示 label
        if label:
            text = f"Detected: {label}"
            cv2.putText(left, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 2)

        # 主畫面合併顯示
        merged = cv2.hconcat([left, right])
        cv2.imshow(self.window_name, merged)

        # 顯示遮罩畫面（自動建立/移動視窗）
        for idx, mask_name in enumerate(self.mask_windows):
            if cv2.getWindowProperty(mask_name, 0) < 0:
                cv2.namedWindow(mask_name)
                cv2.moveWindow(mask_name, 650 * idx, 520)

    def should_quit(self):
        # 按下 q 鍵離開
        return cv2.waitKey(1) & 0xFF == ord('q')

# ====== 目標偵測主函式 ======
def detect_target(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # 轉 HSV
    result_frame = frame.copy()
    mask_total = np.zeros(hsv.shape[:2], dtype=np.uint8)  # 全部遮罩
    detected_labels = []

    for color_name, (lower, upper) in color_ranges.items():
        lower_np = np.array(lower)
        upper_np = np.array(upper)
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
            # 直接在這裡判斷形狀與面積條件
            if num_vertices == 3 and area >= 1500:
                shape = "Triangle"
            elif num_vertices == 4 and 0.8 < aspect_ratio < 1.2 and area >= 1000:
                shape = "Square"
            elif 5 <= num_vertices <= 6 and area >= 1500:
                shape = "Hexagon"

            if shape:
                label = action_map.get((color_name, shape), None)
                if label:
                    detected_labels.append(label)
                    # 畫出框與標籤
                    cv2.rectangle(result_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(result_frame,
                        f"{color_name}-{shape}",
                        (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (255, 255, 255), 2)

    return result_frame, detected_labels, mask_total

# ====== 主程式 ======
def main():
    cap = cv2.VideoCapture(0)  # <<< 這裡可指定攝影機編號
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