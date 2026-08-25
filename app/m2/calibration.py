"""Empirical uncertainty calibration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CalibrationResult:
    """Uncertainty calibration result."""

    raw_uncertainty: float
    calibrated_uncertainty: float
    confidence: float


class UncertaintyCalibrator:
    """Monotonic empirical calibration of model uncertainty using held-out errors."""

    def __init__(self) -> None:
        """Initialize the calibrator."""
        self._errors: list[float] = []

    def fit(self, errors: list[float]) -> None:
        """Fit calibration function to errors."""
        values = sorted(max(0.0, float(x)) for x in errors)
        if not values:
            raise ValueError("at least one calibration error is required")
        self._errors = values

    def transform(self, uncertainty: float) -> CalibrationResult:
        """Transform raw uncertainty to calibrated value."""
        if not self._errors:
            raise RuntimeError("calibrator is not fitted")
        u = max(0.0, float(uncertainty))
        rank = sum(e <= u for e in self._errors) / len(self._errors)
        return CalibrationResult(u, rank, 1.0 - rank)
