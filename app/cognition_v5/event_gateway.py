"""Thalamus-like event gateway: normalize, validate and project observations."""
from __future__ import annotations

from dataclasses import dataclass
from time import monotonic
from typing import Iterable

from .core import Observation
from .world_state import WorldState


@dataclass(frozen=True, slots=True)
class RoutedObservation:
    observation: Observation
    accepted: bool
    reason: str


class EventGateway:
    """Small deterministic boundary between providers and cognition."""

    def __init__(self, *, min_confidence: float = 0.0) -> None:
        if not 0.0 <= min_confidence <= 1.0:
            raise ValueError("min_confidence must be between 0 and 1")
        self.min_confidence = min_confidence

    def route(self, observation: Observation) -> RoutedObservation:
        if observation.confidence < self.min_confidence:
            return RoutedObservation(observation, False, "below confidence threshold")
        if not observation.kind.strip():
            return RoutedObservation(observation, False, "empty observation kind")
        return RoutedObservation(observation, True, "accepted")

    def project(self, state: WorldState, observations: Iterable[Observation]) -> WorldState:
        next_state = state
        for observation in observations:
            routed = self.route(observation)
            if not routed.accepted:
                continue
            next_state = next_state.evolve(**{observation.kind: observation.value})
        return next_state
