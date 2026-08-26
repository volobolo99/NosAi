"""Calibration primitives for deterministic NosTale UI regions.

Calibration stores geometry and expected value ranges; it never guesses values.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Roi:
    x: float
    y: float
    width: float
    height: float

    def __post_init__(self) -> None:
        if not (0 <= self.x <= 1 and 0 <= self.y <= 1):
            raise ValueError("ROI origin must use normalized coordinates")
        if not (0 < self.width <= 1 and 0 < self.height <= 1):
            raise ValueError("ROI dimensions must be in (0, 1]")
        if self.x + self.width > 1 or self.y + self.height > 1:
            raise ValueError("ROI must remain inside normalized frame bounds")

    def pixels(self, frame_width: int, frame_height: int) -> tuple[int, int, int, int]:
        if frame_width <= 0 or frame_height <= 0:
            raise ValueError("frame dimensions must be positive")
        x = round(self.x * frame_width)
        y = round(self.y * frame_height)
        w = round(self.width * frame_width)
        h = round(self.height * frame_height)
        return x, y, max(1, w), max(1, h)


@dataclass(frozen=True)
class BarCalibration:
    """Geometry and semantic constraints for a health/mana bar."""

    roi: Roi
    minimum: int = 0
    maximum: int = 100

    def __post_init__(self) -> None:
        if self.minimum < 0 or self.maximum <= self.minimum:
            raise ValueError("invalid value range")


@dataclass(frozen=True)
class PlayerUiCalibration:
    hp: BarCalibration | None = None
    mp: BarCalibration | None = None


@dataclass(frozen=True)
class CalibrationProfile:
    name: str
    client_width: int
    client_height: int
    player_ui: PlayerUiCalibration

    def __post_init__(self) -> None:
        if self.client_width <= 0 or self.client_height <= 0:
            raise ValueError("calibration dimensions must be positive")
