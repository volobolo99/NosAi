from __future__ import annotations
from dataclasses import dataclass

@dataclass
class MetaLearner:
    """Online normalized-gradient learner for planner scoring weights."""
    weights: dict[str, float]
    learning_rate: float = 0.05
    min_weight: float = 0.0
    max_weight: float = 5.0

    def score(self, features: dict[str, float]) -> float:
        return sum(self.weights.get(k, 0.0) * float(v) for k, v in features.items())

    def update(self, features: dict[str, float], target: float, prediction: float | None = None) -> float:
        pred = self.score(features) if prediction is None else float(prediction)
        error = float(target) - pred
        norm = sum(float(v) ** 2 for v in features.values()) + 1e-8
        step = self.learning_rate * error / norm
        for key, value in features.items():
            self.weights[key] = min(self.max_weight, max(self.min_weight, self.weights.get(key, 0.0) + step * float(value)))
        return error

    def snapshot(self) -> dict[str, float]:
        return dict(self.weights)
