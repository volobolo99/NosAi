from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .evaluation_gate import DeterministicEvaluationGate, EvaluationGateResult
from .safety_orchestrator import SafeCycleResult, SafeZMSIAOrchestrator
from .telemetry import CycleTelemetry, InMemoryTelemetry


@dataclass(frozen=True)
class SafeEvaluatedCycleResult:
    """Combined validation, safety and evaluation result for one cycle."""

    safe_cycle: SafeCycleResult
    evaluation: EvaluationGateResult

    @property
    def accepted(self) -> bool:
        """Return whether both safety and evaluation gates accepted the cycle."""
        return self.safe_cycle.allowed and self.evaluation.accepted


class SafeEvaluatedZMSIAOrchestrator(SafeZMSIAOrchestrator):
    """Full dry-run control loop with validation, safety, evaluation and telemetry."""

    def __init__(self, decision_provider, safety_policy, evaluator=None, telemetry=None) -> None:
        """Create the fully gated dry-run orchestrator."""
        super().__init__(decision_provider, safety_policy)
        self._evaluator = evaluator or DeterministicEvaluationGate()
        self._telemetry = telemetry or InMemoryTelemetry()

    def run_evaluated_once(self, observation: Any) -> SafeEvaluatedCycleResult:
        """Run one cycle, evaluate it, and record the complete gate outcome."""
        safe_cycle = self.run_safe_once(observation)
        evaluation = self._evaluator.evaluate(
            safe_cycle.cycle.state,
            safe_cycle.cycle.decision,
            safe_cycle.cycle.action,
        )
        reasons = list(evaluation.reasons)
        if not safe_cycle.allowed:
            reasons.insert(0, safe_cycle.reason)
        self._telemetry.record(
            CycleTelemetry(
                cycle_id=safe_cycle.cycle.decision.decision_id,
                observation_id=safe_cycle.cycle.observation.observation_id,
                decision_id=safe_cycle.cycle.decision.decision_id,
                action_id=safe_cycle.cycle.action.action_id,
                action_type=safe_cycle.cycle.action.action_type,
                safety_allowed=safe_cycle.allowed,
                evaluation_accepted=evaluation.accepted,
                reasons=tuple(reasons),
            )
        )
        return SafeEvaluatedCycleResult(safe_cycle=safe_cycle, evaluation=evaluation)

    def telemetry_snapshot(self):
        """Return the immutable telemetry snapshot collected by this orchestrator."""
        return self._telemetry.snapshot()
