import serial
import time

# 1. 設定 Arduino 的連接埠與速度
arduino = serial.Serial('COM4', 9600)  # <<<< 請確認你的 Arduino  COM 跟 Baudrate
time.sleep(2)  # 等待 Arduino 重啟
print("Arduino準備好了！請輸入。輸入 Q 可退出程式。")

# 2. 重複讓使用者輸入並傳送
while True:
    command = input("請輸入指令（Q 離開）：").strip().upper()

    if command == 'Q':
        print("離開程式")
        break

    # 不再限制只能 A~F，任何輸入都會傳送
    arduino.write(command.encode())
    print("已傳送：", command)

    time.sleep(6)  # <<< 這裡可以調整等待時間長短
    while arduino.in_waiting > 0:
        response = arduino.readline().decode().strip()
        print("Arduino：", response)

# 3. 關閉連線
arduino.close()
