# main.py
import cv2
import numpy as np
from OpenCV2Arduino import SignalSender, StateManager, AppUI

# ====== Main Parameter Settings ======
COM_PORT = 'COM4'        # <<< Fill in your Arduino COM port here
BAUD_RATE = 9600         # <<< Fill in your Serial Baudrate here
# ====== Camera Settings ======
cap1 = cv2.VideoCapture(0)  # <<< Modify as needed (0 is usually the built-in camera, 1 is external)

# Color + Shape to Arduino command code mapping (modify as needed)
action_map = {
    ('Red', 'Triangle'): 'A',
    ('Red', 'Square'): 'B',
    ('Red', 'Hexagon'): 'C',
    ('Blue', 'Triangle'): 'D',
    ('Blue', 'Square'): 'E',
    ('Blue', 'Hexagon'): 'F',
}

# Set HSV range and minimum area here
color_ranges = {
    "Red": {
        "low": [25, 29, 233],
        "high": [35, 123, 255],
        "min_area": 1500
    },
    "Blue": {
        "low": [54, 84, 129],
        "high": [84, 255, 201],
        "min_area": 1500
    }
}

# ====== Target Detection Main Function ======
def detect_target(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # Convert to HSV
    result_frame = frame.copy()
    mask_total = np.zeros(hsv.shape[:2], dtype=np.uint8)  # Total mask
    detected_labels = []

    for color_name, cfg in color_ranges.items():
        low_np = np.array(cfg["low"])
        high_np = np.array(cfg["high"])
        min_area = cfg.get("min_area", 1000)
        mask = cv2.inRange(hsv, low_np, high_np)  # Generate mask
        mask_total = cv2.bitwise_or(mask_total, mask)
        cv2.imshow(f"{color_name} Mask", mask)  # Show mask

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)  # Polygon approximation
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

# ====== Main Program ======
def main():
    cap = cap1  # Use camera
    sender = SignalSender(port=COM_PORT, baudrate=BAUD_RATE)  # Create Serial sender object
    ui = AppUI()  # Create UI object

    if not cap.isOpened():
        print("[Main] Camera not accessible.")
        return

    print("[Main] System running. Press 'q' to quit.")
    state_manager = StateManager()  # State management (multi-frame stable detection)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        result_frame, labels, mask = detect_target(frame)  # Target detection
        ui.update(frame, result_frame, mask, labels)       # Update UI

        if labels:
            state_manager.update(labels[0])  # Target detected, update state
        else:
            stable_label = state_manager.update(None)  # No detection, check for stable result
            if stable_label:
                print(f"[Main] Stable trigger: {stable_label}")
                sender.send_async(stable_label)  # Asynchronously send signal to Arduino

        if ui.should_quit():
            break

    cap.release()
    cv2.destroyAllWindows()
    sender.close()
    print("[Main] System exited.")

if __name__ == '__main__':
    main()