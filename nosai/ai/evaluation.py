"""Read-only evaluation and feedback metrics for inference outputs (G3.20)."""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class EvaluationResult:
    samples: int
    mean_score: float
    mean_confidence: float
    feedback_rate: float


class InferenceEvaluator:
    """Measures inference quality without changing runtime state."""

    def evaluate(self, results: list[dict[str, object]]) -> EvaluationResult:
        if not isinstance(results, list) or not results:
            raise ValueError("results must be a non-empty list")
        scores: list[float] = []
        confidences: list[float] = []
        feedback = 0
        for item in results:
            if not isinstance(item, dict):
                continue
            score = item.get("score")
            confidence = item.get("confidence")
            if isinstance(score, (int, float)) and isfinite(float(score)):
                scores.append(max(0.0, min(1.0, float(score))))
            if isinstance(confidence, (int, float)) and isfinite(float(confidence)):
                confidences.append(max(0.0, min(1.0, float(confidence))))
            if "feedback" in item:
                feedback += 1
        return EvaluationResult(
            samples=len(results),
            mean_score=sum(scores) / len(scores) if scores else 0.0,
            mean_confidence=sum(confidences) / len(confidences) if confidences else 0.0,
            feedback_rate=feedback / len(results),
        )
