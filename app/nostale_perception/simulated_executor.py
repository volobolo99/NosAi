"""Deterministic executor for replay/simulation only; never touches OS input or the game client."""
from __future__ import annotations

from dataclasses import dataclass

from .autonomy import ExecutionResult, SkillExecutor, SkillRequest
from .game_state import GameState


@dataclass(frozen=True)
class SimulationRule:
    skill: str
    success: bool
    message: str = "simulated"


class SimulatedSkillExecutor(SkillExecutor):
    def __init__(self, rules: list[SimulationRule] | None = None) -> None:
        self.rules = {rule.skill: rule for rule in (rules or [])}
        self.executions: list[str] = []

    def execute(self, request: SkillRequest, state: GameState) -> ExecutionResult:
        rule = self.rules.get(request.skill)
        if rule is None:
            return ExecutionResult(request.skill, False, False, None, "no simulation rule")
        self.executions.append(request.skill)
        return ExecutionResult(request.skill, True, True, rule.success, rule.message)
