# state_manager.py

from collections import deque, Counter

class StateManager:
    def __init__(self, buffer_size=30, cooldown_frames=15):
        self.buffer = deque(maxlen=buffer_size)
        self.last_sent_label = None
        self.sent = False
        self.no_label_count = 0
        self.cooldown_frames = cooldown_frames

    def update(self, new_label):
        """
        每次更新偵測結果（label 為 None 表示物體離開畫面）
        cooldown_frames，避免因畫面閃爍誤判離開
        """
        if new_label is not None:
            self.buffer.append(new_label)
            self.sent = False  # 若有新目標，重置 sent 狀態
            self.no_label_count = 0  # 偵測到物體，重置計數
        else:
            self.no_label_count += 1
            # 只有當 buffer 滿且 cooldown 達標才判定離開
            if (
                len(self.buffer) == self.buffer.maxlen
                and not self.sent
                and self.no_label_count >= self.cooldown_frames
            ):
                label_counts = Counter(self.buffer)
                most_common, count = label_counts.most_common(1)[0]
                self.last_sent_label = most_common
                self.sent = True
                self.buffer.clear()
                self.no_label_count = 0  # 重置
                return most_common
        return None
