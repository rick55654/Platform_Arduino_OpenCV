# signal_sender.py

import serial
import time
import threading

class SignalSender:
    """
    負責與 Arduino 進行序列通訊的類別
    可同步/非同步發送訊號，並自動監聽 Arduino 回傳訊息
    """

    def __init__(self, port='COM5', baudrate=9600):
        """
        初始化，連接指定的序列埠與鮑率
        port: 你的 Arduino COM 埠 (如 'COM7')
        baudrate: 通訊鮑率 (如 9600)
        """
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)  # 等待 Arduino 重置
            print(f"[SignalSender] Connected to {port} at {baudrate} baud.")
            self.running = True
            # 啟動背景執行緒監聽 Arduino 回傳
            threading.Thread(target=self.listen_to_serial, daemon=True).start()
        except serial.SerialException as e:
            print(f"[SignalSender] Error: {e}")
            self.ser = None
            self.running = False

    def send(self, signal: str):
        """
        同步發送訊號到 Arduino
        signal: 欲發送的字串 (如 'A', 'B', ...)
        """
        if self.ser and self.ser.is_open:
            self.ser.write(signal.encode())
            print(f"[SignalSender] Sent: {signal}")

    def send_async(self, signal: str):
        """
        非同步發送訊號（不會阻塞主程式）
        """
        threading.Thread(target=self.send, args=(signal,), daemon=True).start()

    def listen_to_serial(self):
        """
        持續監聽 Arduino 回傳的訊息，並即時顯示
        """
        while self.running and self.ser and self.ser.is_open:
            try:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode(errors='ignore').strip()
                    if line:
                        print(f"[Arduino Response] {line}")
            except Exception as e:
                print(f"[SignalSender] Serial read error: {e}")
                break

    def close(self):
        """
        關閉序列連線，釋放資源
        """
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("[SignalSender] Serial closed.")
