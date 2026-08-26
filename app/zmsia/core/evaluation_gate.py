from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .contracts import Action, Decision, State


@dataclass(frozen=True)
class EvaluationGateResult:
    accepted: bool
    reasons: tuple[str, ...] = ()


class Evaluator(Protocol):
    def evaluate(self, state: State, decision: Decision, action: Action) -> EvaluationGateResult: ...


class DeterministicEvaluationGate:
    """Minimal pre-execution gate: only validated noop actions are accepted."""

    def evaluate(self, state: State, decision: Decision, action: Action) -> EvaluationGateResult:
        if not decision.decision_id:
            return EvaluationGateResult(False, ("missing_decision_id",))
        if not action.action_id:
            return EvaluationGateResult(False, ("missing_action_id",))
        if action.action_type != "noop":
            return EvaluationGateResult(False, ("action_not_allowed_in_dry_run",))
        if not 0.0 <= decision.confidence <= 1.0:
            return EvaluationGateResult(False, ("invalid_decision_confidence",))
        return EvaluationGateResult(True)
