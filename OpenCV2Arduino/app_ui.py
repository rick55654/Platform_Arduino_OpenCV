import cv2

class AppUI:
    def __init__(self, window_name="ARMCtrl Demo"):
        self.window_name = window_name
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        self.mask_windows = ["Red Mask", "Blue Mask"]

    def update(self, original_frame, annotated_frame, mask_frame, label=None):
        left = cv2.resize(annotated_frame, (640, 480))
        right = cv2.cvtColor(cv2.resize(mask_frame, (640, 480)), cv2.COLOR_GRAY2BGR)

        if label:
            text = f"Detected: {label}"
            cv2.putText(left, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 2)

        merged = cv2.hconcat([left, right])
        cv2.imshow(self.window_name, merged)

        for idx, mask_name in enumerate(self.mask_windows):
            if cv2.getWindowProperty(mask_name, 0) < 0:
                cv2.namedWindow(mask_name)
                cv2.moveWindow(mask_name, 650 * idx, 520)

    def should_quit(self):
        return cv2.waitKey(1) & 0xFF == ord('q')