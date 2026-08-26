"""Deterministic, observation-only calibration profiles for NosTale vision.

Calibration is resolution-aware and never sends input or controls the client.
Profiles can be tuned from real NosTale screenshots captured on the target PC.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .entity_detection import Roi, default_rois


@dataclass(frozen=True)
class CalibrationProfile:
    name: str
    width: int
    height: int
    rois: tuple[Roi, ...]
    template_threshold: float = 0.78
    observation_only: bool = True

    def validate_image(self, image: Any) -> None:
        shape = getattr(image, "shape", ())
        if len(shape) < 2:
            raise ValueError("image must expose height/width")
        if shape[1] != self.width or shape[0] != self.height:
            raise ValueError(
                f"profile {self.name!r} expects {self.width}x{self.height}, "
                f"got {shape[1]}x{shape[0]}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "template_threshold": self.template_threshold,
            "observation_only": self.observation_only,
            "rois": [r.__dict__ for r in self.rois],
        }


def profile_for_resolution(width: int, height: int) -> CalibrationProfile:
    """Return a safe baseline; real screenshots should be used to tune ROI bounds."""
    return CalibrationProfile(
        name=f"nostale-{width}x{height}",
        width=width,
        height=height,
        rois=default_rois(),
    )
