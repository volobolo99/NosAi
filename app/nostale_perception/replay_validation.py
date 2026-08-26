"""Replay validation for semantic network decoders and world-model updates."""
from __future__ import annotations

from dataclasses import dataclass

from .network_decoder import DecoderRegistry
from .network_observation import NetworkObservation
from .world_model import WorldModel


@dataclass(frozen=True)
class ReplayValidationResult:
    total: int
    decoded: int
    applied: int
    unknown: int
    apply_failures: int

    @property
    def decode_ratio(self) -> float:
        return self.decoded / self.total if self.total else 0.0

    @property
    def apply_ratio(self) -> float:
        return self.applied / self.decoded if self.decoded else 0.0


def validate_replay(observations: list[NetworkObservation], registry: DecoderRegistry) -> tuple[ReplayValidationResult, WorldModel]:
    model = WorldModel()
    decoded = applied = unknown = failures = 0
    ordered = sorted(observations, key=lambda item: (item.timestamp_ms, item.observation_id))
    for observation in ordered:
        semantic = registry.decode(observation)
        if semantic is None:
            unknown += 1
            continue
        decoded += 1
        if model.apply(semantic):
            applied += 1
        else:
            failures += 1
    return ReplayValidationResult(len(observations), decoded, applied, unknown, failures), model
