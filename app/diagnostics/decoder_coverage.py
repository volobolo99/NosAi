"""Decoder coverage metrics for a validated replay."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from app.nostale_perception.network_decoder import DecoderRegistry
from app.nostale_perception.network_observation import NetworkObservation


@dataclass(frozen=True)
class DecoderCoverageReport:
    total: int
    known: int
    unknown: int
    decode_failures: int
    by_header: dict[str, int]
    unknown_headers: dict[str, int]

    @property
    def decode_ratio(self) -> float:
        return self.known / self.total if self.total else 0.0

    @property
    def unknown_ratio(self) -> float:
        return self.unknown / self.total if self.total else 0.0


def measure_decoder_coverage(observations: list[NetworkObservation], registry: DecoderRegistry) -> DecoderCoverageReport:
    known = unknown = failures = 0
    by_header: Counter[str] = Counter()
    unknown_headers: Counter[str] = Counter()
    for observation in observations:
        try:
            decoded = registry.decode(observation)
        except Exception:
            failures += 1
            unknown_headers[observation.header] += 1
            continue
        if decoded is None:
            unknown += 1
            unknown_headers[observation.header] += 1
            continue
        known += 1
        by_header[observation.header] += 1
    return DecoderCoverageReport(len(observations), known, unknown, failures, dict(sorted(by_header.items())), dict(sorted(unknown_headers.items())))
