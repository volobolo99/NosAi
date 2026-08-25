import random

class PrioritizedReplay:
    def __init__(self, capacity=100000, alpha=0.6, beta=0.4, seed=0):
        if capacity <= 0: raise ValueError("capacity must be positive")
        self.capacity = int(capacity)
        self.alpha = float(alpha)
        self.beta = float(beta)
        self.data = []
        self.priorities = []
        self._cursor = 0
        self.rng = random.Random(seed)

    def add(self, item, priority=1.0):
        p = max(float(priority), 1e-8)
        if len(self.data) < self.capacity:
            self.data.append(item)
            self.priorities.append(p)
        else:
            self.data[self._cursor] = item
            self.priorities[self._cursor] = p
            self._cursor = (self._cursor + 1) % self.capacity

    def sample(self, batch_size):
        if not self.data: raise ValueError("replay is empty")
        n = min(int(batch_size), len(self.data))
        weights = [p ** self.alpha for p in self.priorities]
        total = sum(weights)
        probs = [w / total for w in weights]
        idx = self.rng.choices(range(len(self.data)), weights=probs, k=n)
        isw = [(len(self.data) * probs[i]) ** (-self.beta) for i in idx]
        m = max(isw)
        isw = [x / m for x in isw]
        return [self.data[i] for i in idx], idx, isw

    def update_priorities(self, indices, priorities):
        for i, p in zip(indices, priorities):
            if 0 <= i < len(self.priorities):
                self.priorities[i] = max(float(p), 1e-8)

    def __len__(self):
        return len(self.data)
