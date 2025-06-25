import cv2
import numpy as np
import json
import os
import threading
import tkinter as tk

CONFIG_PATH = os.path.join("OpenCV2Arduino", "color_config.json")

class HSVAdjuster:
    def __init__(self):
        self.color_options = ["Red", "Blue"]
        self.color_name = self.color_options[0]
        self.should_exit = False

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise IOError("Cannot open webcam")

        self.hsv_ranges = self._load_config()
        self._start_tkinter_gui()

    def _load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        return {}

    def _save_config(self, color_name):
        lower = [self.h_min.get(), self.s_min.get(), self.v_min.get()]
        upper = [self.h_max.get(), self.s_max.get(), self.v_max.get()]
        self.hsv_ranges[color_name] = [lower, upper]
        with open(CONFIG_PATH, 'w') as f:
            json.dump(self.hsv_ranges, f, indent=4)
        print(f"[{color_name}] HSV Range saved.")

    def _exit_program(self):
        self.should_exit = True
        self.root.destroy()

    def _start_tkinter_gui(self):
        self.root = tk.Tk()
        self.root.title("HSV 調整與儲存工具")
        self.root.geometry("350x500+1200+100")

        # HSV 拉桿
        tk.Label(self.root, text="Hue Min").pack()
        self.h_min = tk.Scale(self.root, from_=0, to=179, orient=tk.HORIZONTAL)
        self.h_min.set(0)
        self.h_min.pack(fill="x")
        tk.Label(self.root, text="Hue Max").pack()
        self.h_max = tk.Scale(self.root, from_=0, to=179, orient=tk.HORIZONTAL)
        self.h_max.set(179)
        self.h_max.pack(fill="x")
        tk.Label(self.root, text="Sat Min").pack()
        self.s_min = tk.Scale(self.root, from_=0, to=255, orient=tk.HORIZONTAL)
        self.s_min.set(0)
        self.s_min.pack(fill="x")
        tk.Label(self.root, text="Sat Max").pack()
        self.s_max = tk.Scale(self.root, from_=0, to=255, orient=tk.HORIZONTAL)
        self.s_max.set(255)
        self.s_max.pack(fill="x")
        tk.Label(self.root, text="Val Min").pack()
        self.v_min = tk.Scale(self.root, from_=0, to=255, orient=tk.HORIZONTAL)
        self.v_min.set(0)
        self.v_min.pack(fill="x")
        tk.Label(self.root, text="Val Max").pack()
        self.v_max = tk.Scale(self.root, from_=0, to=255, orient=tk.HORIZONTAL)
        self.v_max.set(255)
        self.v_max.pack(fill="x")

        # 直接兩個按鈕存紅色或藍色
        btn_save_red = tk.Button(self.root, text="儲存紅色數值", font=("Arial", 14),
                                 command=lambda: self._save_config("Red"))
        btn_save_red.pack(fill="x", padx=10, pady=5)

        btn_save_blue = tk.Button(self.root, text="儲存藍色數值", font=("Arial", 14),
                                  command=lambda: self._save_config("Blue"))
        btn_save_blue.pack(fill="x", padx=10, pady=5)

        # 關閉按鈕
        btn_exit = tk.Button(self.root, text="關閉程式", font=("Arial", 14),
                             command=self._exit_program)
        btn_exit.pack(fill="x", padx=10, pady=10)

        # 啟動影像顯示執行緒
        threading.Thread(target=self._video_loop, daemon=True).start()
        self.root.mainloop()

    def _video_loop(self):
        while not self.should_exit:
            ret, frame = self.cap.read()
            if not ret:
                break
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower = np.array([self.h_min.get(), self.s_min.get(), self.v_min.get()])
            upper = np.array([self.h_max.get(), self.s_max.get(), self.v_max.get()])
            mask = cv2.inRange(hsv, lower, upper)
            result = cv2.bitwise_and(frame, frame, mask=mask)

            # 輪廓偵測與形狀標註
            result_frame = frame.copy()
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)
                area = cv2.contourArea(cnt)
                num_vertices = len(approx)
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = w / h if h != 0 else 0

                shape = None

                #  ↓↓↓↓↓↓↓可以修改 area 或 num_vertices 的數值↓↓↓↓↓↓↓
                if num_vertices == 3 and area >= 1500:
                    shape = "Triangle"
                elif num_vertices == 4 and 0.8 < aspect_ratio < 1.2 and area >= 1000:
                    shape = "Square"
                elif 5 <= num_vertices <= 6 and area >= 1500:
                    shape = "Hexagon"
                # ↑↑↑↑↑↑↑可以修改 area 或 num_vertices 的數值↑↑↑↑↑↑↑
                
                if shape:
                    cv2.drawContours(result_frame, [approx], -1, (0, 0, 255), 2)
                    cv2.putText(result_frame, f"{shape} Area:{int(area)}", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            vis = np.hstack((result_frame, result))
            cv2.imshow("Preview", vis)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.should_exit = True
                break
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    HSVAdjuster()
