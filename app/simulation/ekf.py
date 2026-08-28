"""Small dependency-free EKF-style estimator for NosAi state fusion.

The architecture specification models a continuous state from actions and
network observations. This implementation keeps the state vector generic and
uses a diagonal covariance, making it safe to run in the base runtime without
requiring NumPy. Adapters can provide a transition function for richer models.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Callable, Sequence

Vector = tuple[float, ...]
Transition = Callable[[Vector, Vector, float], Vector]


@dataclass(frozen=True)
class Observation:
    values: Vector
    variance: Vector
    source: str = "network"

    def __post_init__(self) -> None:
        if len(self.values) != len(self.variance) or not self.values:
            raise ValueError("observation values/variance must have equal non-zero length")
        if any(v < 0 or not isfinite(v) for v in self.variance):
            raise ValueError("observation variance must be finite and non-negative")


@dataclass(frozen=True)
class StateEstimate:
    values: Vector
    variance: Vector
    timestamp: float
    confidence: float


class EKFStateEstimator:
    """Diagonal-covariance EKF approximation for real-time state fusion."""

    def __init__(
        self,
        initial_state: Sequence[float],
        initial_variance: Sequence[float] | None = None,
        process_variance: Sequence[float] | None = None,
        transition: Transition | None = None,
    ) -> None:
        state = tuple(float(x) for x in initial_state)
        if not state:
            raise ValueError("initial_state must not be empty")
        n = len(state)
        self._state = state
        self._variance = tuple(float(x) for x in (initial_variance or [1.0] * n))
        self._process = tuple(float(x) for x in (process_variance or [0.05] * n))
        if len(self._variance) != n or len(self._process) != n:
            raise ValueError("variance vectors must match state length")
        if any(x < 0 for x in (*self._variance, *self._process)):
            raise ValueError("variances must be non-negative")
        self._transition = transition or self._default_transition
        self._timestamp = 0.0

    @staticmethod
    def _default_transition(state: Vector, action: Vector, dt: float) -> Vector:
        # State is position/HP/MP/cooldown-like data; action is an additive
        # delta when supplied. Missing action dimensions are treated as zero.
        return tuple(x + (action[i] * dt if i < len(action) else 0.0) for i, x in enumerate(state))

    @property
    def state(self) -> StateEstimate:
        return StateEstimate(self._state, self._variance, self._timestamp, self.confidence)

    @property
    def confidence(self) -> float:
        mean_variance = sum(self._variance) / len(self._variance)
        return max(0.0, min(1.0, 1.0 / (1.0 + mean_variance)))

    def predict(self, action: Sequence[float] = (), dt: float = 0.05, timestamp: float | None = None) -> StateEstimate:
        if dt <= 0:
            raise ValueError("dt must be positive")
        action_v = tuple(float(x) for x in action)
        self._state = tuple(self._transition(self._state, action_v, dt))
        if len(self._state) != len(self._variance):
            raise ValueError("transition must preserve state dimension")
        self._variance = tuple(p + q * dt for p, q in zip(self._variance, self._process))
        self._timestamp = self._timestamp + dt if timestamp is None else float(timestamp)
        return self.state

    def update(self, observation: Observation, timestamp: float | None = None) -> StateEstimate:
        if len(observation.values) != len(self._state):
            raise ValueError("observation dimension must match state dimension")
        corrected = []
        variances = []
        for prior, prior_var, measured, measurement_var in zip(
            self._state, self._variance, observation.values, observation.variance
        ):
            denom = prior_var + measurement_var
            gain = 1.0 if denom == 0 else prior_var / denom
            corrected.append(prior + gain * (measured - prior))
            variances.append(max(0.0, (1.0 - gain) * prior_var))
        self._state = tuple(corrected)
        self._variance = tuple(variances)
        if timestamp is not None:
            self._timestamp = float(timestamp)
        return self.state

    def step(
        self,
        observation: Observation,
        action: Sequence[float] = (),
        dt: float = 0.05,
        timestamp: float | None = None,
    ) -> StateEstimate:
        self.predict(action, dt, timestamp)
        return self.update(observation, timestamp)
