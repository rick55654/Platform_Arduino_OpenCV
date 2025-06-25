import serial
import time
import threading

# ====== 連接 Arduino ======
arduino = serial.Serial('COM4', 9600)  # 改成你自己的 port
time.sleep(2)  # 等待 Arduino 重啟
print("Arduino準備好了！請輸入。輸入 Q 可退出程式。")

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
    command = input("輸入指令（Q 離開）：").strip().upper()
    if command == 'Q':
        print("離開程式")
        break
    # 不再限制只能 A~F，任何輸入都會傳送
    arduino.write(command.encode())
    print(f"[傳送] {command}")

arduino.close()
