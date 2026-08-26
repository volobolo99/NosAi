"""Coverage accounting for observed versus decoded network traffic."""
from __future__ import annotations

from dataclasses import dataclass

from .network_observation import NetworkObservation
from .network_decoder import DecoderRegistry


@dataclass(frozen=True)
class DecoderCoverage:
    total: int
    decoded: int
    unknown: int
    ratio: float


def measure_coverage(observations: list[NetworkObservation], registry: DecoderRegistry) -> DecoderCoverage:
    decoded = sum(registry.decode(observation) is not None for observation in observations)
    total = len(observations)
    return DecoderCoverage(total, decoded, total - decoded, decoded / total if total else 0.0)
