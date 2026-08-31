"""Observation-only minimap-to-world coordinate calibration."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MinimapCalibration:
    origin_x: float
    origin_y: float
    scale_x: float
    scale_y: float
    rotation_deg: float = 0.0
    confidence: float = 1.0

    def __post_init__(self) -> None:
        if self.scale_x == 0 or self.scale_y == 0:
            raise ValueError("minimap scale cannot be zero")
        if not 0 <= self.confidence <= 1:
            raise ValueError("calibration confidence must be between 0 and 1")


class MinimapWorldMapper:
    """Map minimap pixel coordinates into a calibrated world coordinate frame."""

    def __init__(self, calibration: MinimapCalibration) -> None:
        self.calibration = calibration

    def to_world(self, x: float, y: float) -> tuple[float, float]:
        import math
        dx = (x - self.calibration.origin_x) * self.calibration.scale_x
        dy = (y - self.calibration.origin_y) * self.calibration.scale_y
        angle = math.radians(self.calibration.rotation_deg)
        return (
            dx * math.cos(angle) - dy * math.sin(angle),
            dx * math.sin(angle) + dy * math.cos(angle),
        )

    def metadata(self) -> dict[str, float]:
        return {
            "scale_x": self.calibration.scale_x,
            "scale_y": self.calibration.scale_y,
            "rotation_deg": self.calibration.rotation_deg,
            "confidence": self.calibration.confidence,
        }
