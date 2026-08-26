"""End-to-end deterministic decision cycle for safe simulation."""
from __future__ import annotations

from dataclasses import dataclass

from app.nostale_perception.autonomy import AutonomyLevel, ExecutionResult, SafeSkillGateway, SkillRequest
from app.nostale_perception.game_state import GameState
from app.nostale_perception.simulated_executor import SimulatedSkillExecutor
from .evaluation import EvaluationLedger, CycleEvidence
from .planner import DeterministicPlanner, Goal


@dataclass(frozen=True)
class DecisionCycleResult:
    trace_id: str
    skill: str | None
    execution: ExecutionResult
    blocked: bool
    outcome: str
    evidence: CycleEvidence


class DeterministicDecisionCycle:
    """Planner -> gateway -> simulator -> evaluation. It cannot produce live client input."""

    def __init__(self, executor: SimulatedSkillExecutor, level: AutonomyLevel = AutonomyLevel.ASSISTED, ledger: EvaluationLedger | None = None) -> None:
        self.planner = DeterministicPlanner()
        self.gateway = SafeSkillGateway(level)
        self.executor = executor
        self.evaluation = ledger or EvaluationLedger()

    def run(self, state: GameState, goal: Goal) -> DecisionCycleResult:
        trace = self.planner.plan(state, goal)
        if trace.selected_skill is None:
            result = ExecutionResult("", False, False, None, trace.reason)
            evidence = self.evaluation.evaluate(trace.trace_id, goal.value, result)
            return DecisionCycleResult(trace.trace_id, None, result, True, "decision_blocked", evidence)
        request = SkillRequest(trace.selected_skill, 1.0, trace.reason)
        execution = self.gateway.submit(request, state, self.executor)
        if not execution.accepted:
            outcome, blocked = "execution_blocked", True
        elif execution.success:
            outcome, blocked = "success", False
        else:
            outcome, blocked = "execution_failed", False
        evidence = self.evaluation.evaluate(trace.trace_id, goal.value, execution)
        return DecisionCycleResult(trace.trace_id, trace.selected_skill, execution, blocked, outcome, evidence)
