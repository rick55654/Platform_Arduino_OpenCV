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
        Update detection result each time (label is None means object left the frame).
        cooldown_frames prevents misjudgment of leaving due to flickering.
        """
        if new_label is not None:
            self.buffer.append(new_label)
            self.sent = False  # Reset sent state if a new target is detected
            self.no_label_count = 0  # Reset counter when object is detected
        else:
            self.no_label_count += 1
            # Only when buffer is full and cooldown is reached, consider as left
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
                self.no_label_count = 0  # Reset
                return most_common
        return None
