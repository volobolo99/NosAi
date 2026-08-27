"""Read-only NosTale runtime observation boundary.

This is the first live-runtime integration step: it accepts observations from a
user-controlled telemetry bridge but never sends input, injects code, attaches
for control, or executes game actions.
"""
from __future__ import annotations

from dataclasses import dataclass
from time import monotonic
from typing import Mapping


@dataclass(frozen=True)
class NosTaleObservation:
    timestamp: float
    source: str
    state: Mapping[str, str]


class NosTaleLiveObserver:
    """Fail-closed read-only observer for collecting first real runtime data."""

    def __init__(self, source: str = "external-telemetry-bridge", max_observations: int = 2048) -> None:
        if not source.strip():
            raise ValueError("source must be non-empty")
        if max_observations < 1:
            raise ValueError("max_observations must be positive")
        self._source = source.strip()
        self._max = max_observations
        self._observations: list[NosTaleObservation] = []

    @property
    def capabilities(self) -> frozenset[str]:
        return frozenset({"nos_tale", "live_observation", "read_only", "telemetry"})

    @property
    def execution_enabled(self) -> bool:
        return False

    def ingest(self, state: Mapping[str, str]) -> NosTaleObservation:
        """Record an externally supplied observation; never executes a command."""
        clean = {str(k): str(v) for k, v in state.items()}
        observation = NosTaleObservation(monotonic(), self._source, clean)
        self._observations.append(observation)
        if len(self._observations) > self._max:
            del self._observations[: len(self._observations) - self._max]
        return observation

    def observations(self) -> tuple[NosTaleObservation, ...]:
        return tuple(self._observations)

    def latest(self) -> NosTaleObservation | None:
        return self._observations[-1] if self._observations else None
