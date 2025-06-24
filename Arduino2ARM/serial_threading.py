import serial
import threading

# ====== 連接 Arduino ======
arduino = serial.Serial('COM4', 9600)  # 改成你自己的 port
print("已連線到 Arduino，輸入 A~F 傳送，Q 離開")

# ====== 背景監聽 Arduino 回傳 ======
def listen_from_arduino():
    while True:
        if arduino.in_waiting > 0:
            message = arduino.readline().decode().strip()
            print(f"\n[收到] {message}")

# 啟動背景監聽執行緒
listen_thread = threading.Thread(target=listen_from_arduino, daemon=True)
listen_thread.start()

# ====== 主迴圈：輸入並傳送指令 ======
while True:
    command = input("輸入 A~F（Q 離開）：").strip().upper()
    if command == 'Q':
        print("離開程式")
        break
    if command in ['A', 'B', 'C', 'D', 'E', 'F']:
        arduino.write(command.encode())
        print(f"[傳送] {command}")
    else:
        print("只能輸入 A~F 或 Q")

arduino.close()
