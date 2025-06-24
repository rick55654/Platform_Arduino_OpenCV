import serial
import time

# 1. 設定 Arduino 的連接埠與速度
arduino = serial.Serial('COM4', 9600)  # 請確認你的 Arduino 是 COM 幾
time.sleep(2)  # 等待 Arduino 重啟

print("準備好了！請輸入 A ~ F 來控制 Arduino。輸入 Q 可退出程式。")

# 2. 重複讓使用者輸入並傳送
while True:
    command = input("請輸入指令 (A-F)：").strip().upper()

    if command == 'Q':
        print("離開程式")
        break

    # 只允許 A~F
    if command in ['A', 'B', 'C', 'D', 'E', 'F']:
        arduino.write(command.encode())  # 傳送字元給 Arduino
        print("已傳送：", command)

        # 嘗試讀取 Arduino 回傳的多筆資料
        time.sleep(6)  # 稍等一下讓 Arduino 有時間回傳
        while arduino.in_waiting > 0:
            response = arduino.readline().decode().strip()
            print("Arduino：", response)
            # raw_bytes = arduino.readline()
            # print("【Step 1】Raw bytes：", repr(raw_bytes))
            # decoded_str = raw_bytes.decode()
            # print("【Step 2】Decoded：", repr(decoded_str))
            # cleaned_str = decoded_str.strip()
            # print("【Step 3】Cleaned：", repr(cleaned_str))
    else:
        print("請輸入 A ~ F 的字元。")

# 3. 關閉連線
arduino.close()
