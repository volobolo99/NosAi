
from collections import deque


class WorkingMemory:
    def __init__(self, max_items=100):
        self.items = deque(maxlen=max_items)

    def push(self, item):
        self.items.append(item)

    def snapshot(self):
        return list(self.items)

    def clear(self):
        self.items.clear()
