"""Provider-neutral decoded observation contract for NosTale perception.

The decoder boundary deliberately contains no socket/process-hook implementation:
raw transport adapters can translate their data into this immutable contract.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class DecodedObservation:
    """A validated observation emitted by a perception/decoder provider."""

    observation_id: str
    kind: str
    payload: Mapping[str, Any]
    confidence: float
    source: str

    def __post_init__(self) -> None:
        if not self.observation_id:
            raise ValueError("observation_id must not be empty")
        if not self.kind:
            raise ValueError("kind must not be empty")
        if not self.source:
            raise ValueError("source must not be empty")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        object.__setattr__(self, "confidence", float(self.confidence))
        object.__setattr__(self, "payload", dict(self.payload))
