"""Deterministic, read-only evaluation harness for G3.21."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from math import isfinite


@dataclass(frozen=True)
class HarnessReport:
    samples: int
    valid: int
    invalid: int
    mean_score: float
    mean_confidence: float
    feedback_rate: float
    dataset_digest: str


class EvaluationHarness:
    """Compares recorded inference outputs without invoking runtime actions."""

    def run(self, samples: list[dict[str, object]]) -> HarnessReport:
        if not isinstance(samples, list) or not samples:
            raise ValueError("samples must be a non-empty list")
        valid = invalid = feedback = 0
        scores: list[float] = []
        confidences: list[float] = []
        canonical_items: list[dict[str, object]] = []
        for item in samples:
            if not isinstance(item, dict):
                invalid += 1
                continue
            score, confidence = item.get("score"), item.get("confidence")
            if not all(isinstance(v, (int, float)) and isfinite(float(v)) for v in (score, confidence)):
                invalid += 1
                continue
            valid += 1
            scores.append(max(0.0, min(1.0, float(score))))
            confidences.append(max(0.0, min(1.0, float(confidence))))
            feedback += int("feedback" in item)
            canonical_items.append(item)
        canonical = json.dumps(canonical_items, sort_keys=True, separators=(",", ":"), default=str)
        return HarnessReport(
            samples=len(samples), valid=valid, invalid=invalid,
            mean_score=sum(scores) / valid if valid else 0.0,
            mean_confidence=sum(confidences) / valid if valid else 0.0,
            feedback_rate=feedback / valid if valid else 0.0,
            dataset_digest=sha256(canonical.encode()).hexdigest(),
        )
