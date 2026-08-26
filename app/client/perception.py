"""Deterministic first-stage perception for live NosTale observations.

The initial implementation intentionally does not claim to recognize game
entities. It validates the capture geometry and produces quality metadata so a
future local CV model can be added without changing the observation contract.
"""
from __future__ import annotations

from dataclasses import dataclass

from .observation import ObservationFrame


@dataclass(frozen=True)
class PerceptionResult:
    timestamp_ns: int
    frame_width: int
    frame_height: int
    frame_available: bool
    quality: str
    detections: tuple[dict, ...] = ()
    confidence: float = 0.0


def perceive(frame: ObservationFrame) -> PerceptionResult:
    """Validate one frame and return a safe, deterministic perception result."""
    available = bool(frame.image) and frame.width > 0 and frame.height > 0
    if not available:
        return PerceptionResult(
            timestamp_ns=frame.timestamp_ns,
            frame_width=frame.width,
            frame_height=frame.height,
            frame_available=False,
            quality="non_disponibile",
        )
    return PerceptionResult(
        timestamp_ns=frame.timestamp_ns,
        frame_width=frame.width,
        frame_height=frame.height,
        frame_available=True,
        quality="acquisito",
        confidence=1.0,
    )
