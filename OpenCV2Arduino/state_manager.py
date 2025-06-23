# state_manager.py

from collections import deque, Counter

class StateManager:
    def __init__(self, buffer_size=30):
        self.buffer = deque(maxlen=buffer_size)
        self.last_sent_label = None
        self.sent = False

    def update(self, new_label):
        """
        每次更新偵測結果（label 為 None 表示物體離開畫面）
        """
        if new_label is not None:
            self.buffer.append(new_label)
            self.sent = False  # 若有新目標，重置 sent 狀態
        else:
            # 如果目前 buffer 已滿且還沒送過，表示剛離開畫面
            if len(self.buffer) == self.buffer.maxlen and not self.sent:
                label_counts = Counter(self.buffer)
                most_common, count = label_counts.most_common(1)[0]
                self.last_sent_label = most_common
                self.sent = True
                self.buffer.clear()
                return most_common
        return None
