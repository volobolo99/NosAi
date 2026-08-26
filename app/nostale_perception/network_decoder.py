"""Versioned, read-only packet decoding primitives.

Decoders transform already-observed packet records into semantic observations.
They never capture, inject, modify, or replay network traffic themselves.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from .network_observation import NetworkObservation


@dataclass(frozen=True)
class DecodedObservation:
    source_observation_id: str
    kind: str
    payload: Mapping[str, object]
    confidence: float
    decoder_version: str


Decoder = Callable[[NetworkObservation], DecodedObservation | None]


class DecoderRegistry:
    def __init__(self) -> None:
        self._decoders: dict[str, Decoder] = {}

    def register(self, header: str, decoder: Decoder) -> None:
        if not header or header in self._decoders:
            raise ValueError("header must be non-empty and unique")
        self._decoders[header] = decoder

    def decode(self, observation: NetworkObservation) -> DecodedObservation | None:
        decoder = self._decoders.get(observation.header)
        return decoder(observation) if decoder else None

    def known_headers(self) -> tuple[str, ...]:
        return tuple(sorted(self._decoders))
