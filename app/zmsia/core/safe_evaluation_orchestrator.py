from __future__ import annotations

from dataclasses import dataclass

from .evaluation_gate import DeterministicEvaluationGate, EvaluationGateResult
from .safety_orchestrator import SafeCycleResult, SafeZMSIAOrchestrator
from .telemetry import CycleTelemetry, InMemoryTelemetry


@dataclass(frozen=True)
class SafeEvaluatedCycleResult:
    safe_cycle: SafeCycleResult
    evaluation: EvaluationGateResult

    @property
    def accepted(self) -> bool:
        return self.safe_cycle.allowed and self.evaluation.accepted


class SafeEvaluatedZMSIAOrchestrator(SafeZMSIAOrchestrator):
    """Full dry-run control loop with validation, safety, evaluation and telemetry."""

    def __init__(self, decision_provider, safety_policy, evaluator=None, telemetry=None) -> None:
        super().__init__(decision_provider, safety_policy)
        self._evaluator = evaluator or DeterministicEvaluationGate()
        self._telemetry = telemetry or InMemoryTelemetry()

    def run_evaluated_once(self, observation: object) -> SafeEvaluatedCycleResult:
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
                safety_allowed=safe_cycle.allowed,
                evaluation_accepted=evaluation.accepted,
                reasons=tuple(reasons),
            )
        )
        return SafeEvaluatedCycleResult(safe_cycle=safe_cycle, evaluation=evaluation)

    def telemetry_snapshot(self):
        return self._telemetry.snapshot()
