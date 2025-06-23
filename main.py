# main.py
import cv2
from OpenCV2Arduino import detect_target, SignalSender, AppUI, StateManager

COM_PORT = 'COM7'
BAUD_RATE = 9600

def main():
    cap = cv2.VideoCapture(0)
    sender = SignalSender(port=COM_PORT, baudrate=BAUD_RATE)
    ui = AppUI()

    if not cap.isOpened():
        print("[Main] Camera not accessible.")
        return

    print("[Main] System running. Press 'q' to quit.")
    state_manager = StateManager()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        result_frame, labels, mask = detect_target(frame)
        ui.update(frame, result_frame, mask, labels)

        # 修改：更新 label 狀態，並於物體消失時判斷是否觸發
        if labels:
            state_manager.update(labels[0])  # 加入最新 label
        else:
            stable_label = state_manager.update(None)  # 無偵測物時嘗試觸發
            if stable_label:
                print(f"[Main] 穩定觸發：{stable_label}")
                sender.send_async(stable_label)

        if ui.should_quit():
            break

    cap.release()
    cv2.destroyAllWindows()
    sender.close()
    print("[Main] System exited.")

if __name__ == '__main__':
    main()