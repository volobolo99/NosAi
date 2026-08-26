"""Deterministic UI bar detectors for replay-first NosTale perception."""
from __future__ import annotations

from dataclasses import dataclass

from .calibration import BarCalibration
from .perception import Frame


@dataclass(frozen=True)
class BarObservation:
    value: int | None
    maximum: int | None
    fill_ratio: float | None
    confidence: float
    reason: str


class PixelBarDetector:
    """Estimate a bar fill from pixel intensity without OCR or ML.

    The detector intentionally accepts a caller-provided predicate for a bar pixel.
    This makes colour/theme rules testable and avoids baking one UI skin into the
    perception core.
    """

    def __init__(self, calibration: BarCalibration, pixel_is_fill) -> None:
        self._calibration = calibration
        self._pixel_is_fill = pixel_is_fill

    def detect(self, frame: Frame) -> BarObservation:
        if not frame.pixels:
            return BarObservation(None, None, None, 0.0, "pixels-unavailable")
        x, y, width, height = self._calibration.roi.pixels(frame.width, frame.height)
        if len(frame.pixels) != frame.width * frame.height * 4:
            return BarObservation(None, None, None, 0.0, "unsupported-pixel-layout")

        row_count = 0
        fill_count = 0
        for py in range(y, min(y + height, frame.height)):
            row_count += 1
            for px in range(x, min(x + width, frame.width)):
                offset = (py * frame.width + px) * 4
                bgra = frame.pixels[offset:offset + 4]
                if self._pixel_is_fill(bgra):
                    fill_count += 1

        area = width * height
        if row_count == 0 or area <= 0:
            return BarObservation(None, None, None, 0.0, "empty-roi")
        ratio = max(0.0, min(1.0, fill_count / area))
        value = round(self._calibration.minimum + ratio * (self._calibration.maximum - self._calibration.minimum))
        confidence = min(1.0, 0.5 + min(0.5, area / 10000))
        return BarObservation(value, self._calibration.maximum, ratio, confidence, "pixel-fill")
