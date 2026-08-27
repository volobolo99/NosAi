"""Deterministic replay execution for protected regression scenarios."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable

from .replay import ReplayCase


@dataclass(frozen=True, slots=True)
class ReplayResult:
    case_id: str
    passed: bool
    expected: dict[str, Any]
    actual: dict[str, Any]
    detail: str


ReplayEvaluator = Callable[[dict[str, Any]], dict[str, Any]]


class ReplayRunner:
    """Run protected scenarios against a deterministic evaluator.

    The evaluator is deliberately injected: replay never executes researched
    source code by itself. A real candidate executor is supplied by the
    sandbox/regression layer.
    """

    def __init__(self, evaluator: ReplayEvaluator) -> None:
        self.evaluator = evaluator

    def run(self, cases: Iterable[ReplayCase]) -> list[ReplayResult]:
        results: list[ReplayResult] = []
        for case in cases:
            try:
                actual = self.evaluator(case.scenario)
                passed = _matches_expected(case.expected, actual)
                detail = "expected output matched" if passed else "expected output mismatch"
            except Exception as exc:  # replay must report failures, not abort the suite
                actual = {"exception_type": type(exc).__name__, "exception": str(exc)}
                passed = False
                detail = f"replay evaluator raised {type(exc).__name__}: {exc}"
            results.append(ReplayResult(case.case_id, passed, case.expected, actual, detail))
        return results


def _matches_expected(expected: dict[str, Any], actual: dict[str, Any]) -> bool:
    """Compare the declared expected fields without requiring extra telemetry fields."""
    return all(actual.get(key) == value for key, value in expected.items())


def replay_passed(results: Iterable[ReplayResult]) -> bool:
    return all(result.passed for result in results)
