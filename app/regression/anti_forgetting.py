"""Anti-forgetting validation for candidate models and strategies."""

from __future__ import annotations

import logging
from typing import Mapping

LOGGER = logging.getLogger(__name__)

DEFAULT_MAX_DEGRADATION = 0.05


def verify_retention(
    current_model_metrics: Mapping[str, float],
    baseline_metrics: Mapping[str, float],
    max_degradation: float = DEFAULT_MAX_DEGRADATION,
) -> bool:
    """Return whether protected-task metrics remain within the allowed degradation.

    Metrics are interpreted as higher-is-better. Missing baseline metrics are ignored;
    non-numeric values and an invalid threshold raise ``ValueError``.
    """
    if max_degradation < 0:
        raise ValueError("max_degradation must be non-negative")

    for task, baseline in baseline_metrics.items():
        if task not in current_model_metrics:
            continue
        current = current_model_metrics[task]
        if not isinstance(current, (int, float)) or not isinstance(baseline, (int, float)):
            raise ValueError(f"non-numeric metric for task {task!r}")
        if baseline == 0:
            degradation = 0.0 if current >= baseline else float("inf")
        else:
            degradation = (baseline - current) / abs(baseline)
        if degradation > max_degradation:
            LOGGER.warning(
                "anti-forgetting rollback required: task=%s baseline=%s current=%s degradation=%.4f",
                task, baseline, current, degradation,
            )
            return False
    return True
