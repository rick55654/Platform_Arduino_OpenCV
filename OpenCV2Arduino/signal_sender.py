# signal_sender.py

import serial
import time
import threading

class SignalSender:
    """
    Class responsible for serial communication with Arduino.
    Supports synchronous/asynchronous signal sending and automatically listens for Arduino responses.
    """

    def __init__(self, port='COM5', baudrate=9600):
        """
        Initialize and connect to the specified serial port and baudrate.
        port: Your Arduino COM port (e.g., 'COM7')
        baudrate: Communication baudrate (e.g., 9600)
        """
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset
            print(f"[SignalSender] Connected to {port} at {baudrate} baud.")
            self.running = True
            # Start background thread to listen for Arduino responses
            threading.Thread(target=self.listen_to_serial, daemon=True).start()
        except serial.SerialException as e:
            print(f"[SignalSender] Error: {e}")
            self.ser = None
            self.running = False

    def send(self, signal: str):
        """
        Synchronously send a signal to Arduino.
        signal: String to send (e.g., 'A', 'B', ...)
        """
        if self.ser and self.ser.is_open:
            self.ser.write(signal.encode())
            print(f"[SignalSender] Sent: {signal}")

    def send_async(self, signal: str):
        """
        Asynchronously send a signal (non-blocking).
        """
        threading.Thread(target=self.send, args=(signal,), daemon=True).start()

    def listen_to_serial(self):
        """
        Continuously listen for Arduino responses and display them in real time.
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
        Close the serial connection and release resources.
        """
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("[SignalSender] Serial closed.")
