"""Ground-truth metrics for replayed NosTale perception."""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class NumericMetric:
    count: int
    mae: float | None
    rmse: float | None
    within_tolerance: float | None


def numeric_metric(actual: list[float], expected: list[float], tolerance: float) -> NumericMetric:
    if len(actual) != len(expected):
        raise ValueError("actual and expected lengths must match")
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")
    if not actual:
        return NumericMetric(0, None, None, None)
    errors = [abs(a - e) for a, e in zip(actual, expected)]
    return NumericMetric(
        count=len(errors),
        mae=sum(errors) / len(errors),
        rmse=sqrt(sum(error * error for error in errors) / len(errors)),
        within_tolerance=sum(error <= tolerance for error in errors) / len(errors),
    )


def classification_accuracy(actual: list[str | None], expected: list[str | None]) -> float | None:
    if len(actual) != len(expected):
        raise ValueError("actual and expected lengths must match")
    if not actual:
        return None
    return sum(a == e for a, e in zip(actual, expected)) / len(actual)
