"""End-to-end deterministic decision cycle for safe simulation."""
from __future__ import annotations

from dataclasses import dataclass

from app.nostale_perception.autonomy import AutonomyLevel, ExecutionResult, SafeSkillGateway, SkillRequest
from app.nostale_perception.game_state import GameState
from app.nostale_perception.simulated_executor import SimulatedSkillExecutor
from .planner import DeterministicPlanner, Goal


@dataclass(frozen=True)
class DecisionCycleResult:
    trace_id: str
    skill: str | None
    execution: ExecutionResult
    blocked: bool
    outcome: str


class DeterministicDecisionCycle:
    """Planner -> gateway -> simulator. It cannot produce live client input."""

    def __init__(self, executor: SimulatedSkillExecutor, level: AutonomyLevel = AutonomyLevel.ASSISTED) -> None:
        self.planner = DeterministicPlanner()
        self.gateway = SafeSkillGateway(level)
        self.executor = executor

    def run(self, state: GameState, goal: Goal) -> DecisionCycleResult:
        trace = self.planner.plan(state, goal)
        if trace.selected_skill is None:
            result = ExecutionResult("", False, False, None, trace.reason)
            return DecisionCycleResult(trace.trace_id, None, result, True, "decision_blocked")
        request = SkillRequest(trace.selected_skill, 1.0, trace.reason)
        execution = self.gateway.submit(request, state, self.executor)
        if not execution.accepted:
            return DecisionCycleResult(trace.trace_id, trace.selected_skill, execution, True, "execution_blocked")
        if execution.success:
            return DecisionCycleResult(trace.trace_id, trace.selected_skill, execution, False, "success")
        return DecisionCycleResult(trace.trace_id, trace.selected_skill, execution, False, "execution_failed")
