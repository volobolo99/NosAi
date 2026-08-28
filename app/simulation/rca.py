"""50 Hz telemetry black-box and post-mortem root-cause primitives."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import sqrt
from typing import Iterable, Sequence


@dataclass(frozen=True)
class TelemetrySample:
    timestamp: float
    real_state: tuple[float, ...]
    simulated_state: tuple[float, ...]
    event: str = ""


@dataclass(frozen=True)
class Divergence:
    timestamp: float
    error_norm: float
    sample: TelemetrySample


class TelemetryBuffer:
    """Fixed-size circular telemetry store; default capacity is 120 s at 50 Hz."""

    def __init__(self, capacity: int = 6000) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._samples: deque[TelemetrySample] = deque(maxlen=capacity)

    def append(self, sample: TelemetrySample) -> None:
        if len(sample.real_state) != len(sample.simulated_state) or not sample.real_state:
            raise ValueError("telemetry states must have equal non-zero dimensions")
        self._samples.append(sample)

    def snapshot(self) -> tuple[TelemetrySample, ...]:
        return tuple(self._samples)


class PostMortemRCA:
    """Find the first state divergence beyond epsilon."""

    @staticmethod
    def first_divergence(samples: Iterable[TelemetrySample], epsilon: float) -> Divergence | None:
        if epsilon < 0:
            raise ValueError("epsilon cannot be negative")
        for sample in sorted(samples, key=lambda item: item.timestamp):
            error = sqrt(sum((a - b) ** 2 for a, b in zip(sample.real_state, sample.simulated_state)))
            if error > epsilon:
                return Divergence(sample.timestamp, error, sample)
        return None

    @staticmethod
    def bayesian_update(prior: dict[str, float], likelihood: dict[str, float]) -> dict[str, float]:
        """Discrete posterior update P(theta|D) proportional to likelihood*prior."""
        if not prior or set(prior) != set(likelihood):
            raise ValueError("prior and likelihood must contain the same non-empty keys")
        weights = {key: max(0.0, prior[key]) * max(0.0, likelihood[key]) for key in prior}
        total = sum(weights.values())
        if total == 0:
            raise ValueError("posterior has zero probability mass")
        return {key: value / total for key, value in weights.items()}
