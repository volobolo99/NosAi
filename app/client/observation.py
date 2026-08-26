"""Normalized live observation primitives for the NosTale client.

This layer deliberately separates Windows capture from perception. It turns a
raw client window observation into a stable frame contract that the dashboard,
World Model and future local vision pipeline can consume without depending on
Windows APIs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic_ns
from typing import Any, Mapping


@dataclass(frozen=True)
class ObservationFrame:
    """One immutable observation of the visible NosTale client."""

    timestamp_ns: int
    pid: int
    window: Mapping[str, int]
    image: bytes | None = None
    width: int = 0
    height: int = 0
    source: str = "windows_observation"
    confidence: float = 1.0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def as_dict(self, *, include_image: bool = False) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "timestamp_ns": self.timestamp_ns,
            "pid": self.pid,
            "window": dict(self.window),
            "width": self.width,
            "height": self.height,
            "source": self.source,
            "confidence": self.confidence,
            "metadata": dict(self.metadata),
        }
        if include_image and self.image is not None:
            payload["image_bytes"] = self.image
        return payload


def build_observation(*, pid: int, window: Mapping[str, int], image: bytes | None = None,
                      width: int = 0, height: int = 0, metadata: Mapping[str, Any] | None = None,
                      timestamp_ns: int | None = None) -> ObservationFrame:
    """Build a normalized frame without performing capture or inference."""
    return ObservationFrame(
        timestamp_ns=monotonic_ns() if timestamp_ns is None else timestamp_ns,
        pid=pid,
        window=dict(window),
        image=image,
        width=width,
        height=height,
        metadata=dict(metadata or {}),
    )
