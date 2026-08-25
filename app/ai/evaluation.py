"""Offline evaluation primitives for AI decision quality and regressions.

The evaluator is intentionally provider-neutral: it accepts a callable decision
provider and never executes actions against the real client.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
import json
import time
from typing import Any, Callable, Mapping


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    category: str
    state: Mapping[str, Any]
    objective: str
    expected_action_type: str
    expected_valid: bool = True


@dataclass(frozen=True)
class EvaluationResult:
    case_id: str
    category: str
    passed: bool
    valid: bool
    latency_ms: float
    fallback_used: bool
    action_type: str | None
    error: str | None = None


class EvaluationRunner:
    """Run deterministic/mock AI evaluations without touching the game client."""

    def __init__(self, decision_provider: Callable[[Mapping[str, Any], str], Mapping[str, Any]]):
        self._decision_provider = decision_provider

    def run(self, cases: list[EvaluationCase]) -> list[EvaluationResult]:
        results: list[EvaluationResult] = []
        for case in cases:
            started = time.perf_counter()
            fallback_used = False
            error: str | None = None
            decision: Mapping[str, Any] | None = None
            try:
                decision = self._decision_provider(case.state, case.objective)
                fallback_used = bool(decision.get("fallback_used", False))
                action_type = decision.get("action_type")
                valid = bool(decision.get("valid", action_type is not None))
                passed = valid == case.expected_valid and action_type == case.expected_action_type
            except Exception as exc:  # evaluation must report failures, not abort the suite
                valid = False
                action_type = None
                passed = not case.expected_valid
                error = f"{type(exc).__name__}: {exc}"
            latency_ms = (time.perf_counter() - started) * 1000
            results.append(
                EvaluationResult(
                    case_id=case.case_id,
                    category=case.category,
                    passed=passed,
                    valid=valid,
                    latency_ms=latency_ms,
                    fallback_used=fallback_used,
                    action_type=action_type,
                    error=error,
                )
            )
        return results


def summarize(results: list[EvaluationResult]) -> dict[str, Any]:
    total = len(results)
    passed = sum(result.passed for result in results)
    fallbacks = sum(result.fallback_used for result in results)
    latencies = [result.latency_ms for result in results]
    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": passed / total if total else 1.0,
        "fallback_rate": fallbacks / total if total else 0.0,
        "latency_ms": {
            "min": min(latencies) if latencies else 0.0,
            "max": max(latencies) if latencies else 0.0,
            "avg": sum(latencies) / len(latencies) if latencies else 0.0,
        },
    }


def write_report(path: str, results: list[EvaluationResult]) -> None:
    payload = {
        "results": [asdict(result) for result in results],
        "summary": summarize(results),
    }
    with open(path, "w", encoding="utf-8") as report:
        json.dump(payload, report, indent=2, sort_keys=True)
        report.write("\n")
