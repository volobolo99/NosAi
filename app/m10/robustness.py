"""Robustness verification engine for adversarial stress-testing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable


@dataclass(frozen=True)
class RobustnessReport:
    """Robustness evaluation summary."""

    adversarial_score: float
    rare_event_score: float
    observation_quality: float
    failure_probability: float
    safe_fallback: bool
    stress_cases: int = 0


class RobustnessEngine:
    """Robustness adversarial and stress testing engine."""

    def adversarial_score(self, nominal: float, perturbed: Iterable[float]) -> float:
        """Compute adversarial robustness score."""
        rows = list(perturbed)
        if not rows:
            return 1.0
        return max(0.0, min(1.0, 1.0 - sum(abs(x - nominal) for x in rows) / len(rows)))

    def rare_event_score(self, failures: int, trials: int) -> float:
        """Compute rare event failure rate."""
        if trials <= 0:
            return 1.0
        return max(0.0, min(1.0, 1.0 - failures / trials))

    def observation_quality(
        self, observed: Iterable[float], expected: Iterable[float]
    ) -> float:
        """Compute observation quality via error."""
        a = list(observed)
        b = list(expected)
        if not a or len(a) != len(b):
            return 0.0
        err = sum(abs(x - y) for x, y in zip(a, b)) / len(a)
        return 1 / (1 + err)

    def predict_failure(
        self, risk: float, uncertainty: float, threshold: float = 0.7
    ) -> bool:
        """Predict whether action will fail based on risk and uncertainty."""
        return 0.7 * risk + 0.3 * uncertainty >= threshold

    def safe_action(
        self,
        preferred: Any,
        fallback: Any,
        *,
        failure_probability: float,
        threshold: float = 0.7,
    ) -> Any:
        """Select safe action fallback if failure probability is too high."""
        return fallback if failure_probability >= threshold else preferred

    def perturbations(
        self, value: float, epsilon: float = 0.1, count: int = 5
    ) -> list[float]:
        """Generate adversarial perturbation values."""
        return [value - epsilon, value + epsilon] + [
            value + (epsilon * (i - (count - 1) / 2) / (count or 1)) for i in range(count)
        ]

    def stress(
        self,
        fn: Callable[[Any], Any],
        cases: Iterable[Any],
        fallback: Any = None,
    ) -> tuple[list[Any], int]:
        """Stress-test function on cases; return outputs and failure count."""
        outputs = []
        failures = 0
        for case in cases:
            try:
                outputs.append(fn(case))
            except Exception:
                failures += 1
                outputs.append(fallback)
        return outputs, failures

    def report(
        self,
        nominal: float,
        perturbed: Iterable[float],
        failures: int,
        trials: int,
        observed: Iterable[float],
        expected: Iterable[float],
        risk: float,
        uncertainty: float,
    ) -> RobustnessReport:
        """Generate comprehensive robustness report."""
        fp = 0.7 * risk + 0.3 * uncertainty
        return RobustnessReport(
            self.adversarial_score(nominal, perturbed),
            self.rare_event_score(failures, trials),
            self.observation_quality(observed, expected),
            fp,
            fp >= 0.7,
            len(list(perturbed)),
        )
