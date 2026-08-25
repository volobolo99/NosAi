from __future__ import annotations
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class CalibrationResult:
    raw_uncertainty: float
    calibrated_uncertainty: float
    confidence: float

class UncertaintyCalibrator:
    """Monotonic empirical calibration of model uncertainty using held-out errors."""
    def __init__(self): self._errors=[]
    def fit(self, errors):
        values=sorted(max(0.0,float(x)) for x in errors)
        if not values: raise ValueError("at least one calibration error is required")
        self._errors=values
    def transform(self, uncertainty: float) -> CalibrationResult:
        if not self._errors: raise RuntimeError("calibrator is not fitted")
        u=max(0.0,float(uncertainty)); rank=sum(e<=u for e in self._errors)/len(self._errors)
        return CalibrationResult(u,rank,1.0-rank)
