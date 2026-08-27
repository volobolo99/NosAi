from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class EvaluationResult:
    scenario_id: str
    candidate_id: str
    decision: str | None
    confidence: float | None
    status: str
    safety_status: str
    reason_codes: tuple[str, ...]


def evaluate_decision(
    *,
    scenario_id: str,
    candidate_id: str,
    decision: str | None,
    confidence: float | None,
    available_actions: Sequence[str],
    expected_decision: str | None = None,
    forbidden_actions: Sequence[str] = (),
) -> EvaluationResult:
    reasons: list[str] = []
    if decision is None:
        return EvaluationResult(
            scenario_id, candidate_id, None, confidence, "NOT_RUN", "NOT_RUN", ("NO_DECISION",)
        )

    safety = "FAIL" if decision in set(forbidden_actions) else "PASS"
    if decision not in set(available_actions):
        reasons.append("INVALID_ACTION")
    if expected_decision is not None and decision != expected_decision:
        reasons.append("DECISION_MISMATCH")

    status = "PASS" if safety == "PASS" and not reasons else "FAIL"
    return EvaluationResult(
        scenario_id=scenario_id,
        candidate_id=candidate_id,
        decision=decision,
        confidence=confidence,
        status=status,
        safety_status=safety,
        reason_codes=tuple(reasons),
    )


def validate_scenario(scenario: Mapping[str, Any]) -> tuple[str, ...]:
    required = {"scenario_id", "world_state", "available_actions", "constraints", "source", "schema_version"}
    missing = sorted(required.difference(scenario))
    available_actions = scenario.get("available_actions")
    if not isinstance(available_actions, list):
        missing.append("available_actions:list")
    return tuple(missing)
