"""End-to-end simulated autonomy cycle: decide, execute in simulation, evaluate, learn."""
from __future__ import annotations

from dataclasses import dataclass

from .autonomy import AutonomyLevel, SafeSkillGateway, SkillRequest
from .game_state import GameState
from .simulated_executor import SimulatedSkillExecutor
from .skill_ledger import SkillLedger


@dataclass(frozen=True)
class AutonomyCycleResult:
    skill: str
    accepted: bool
    executed: bool
    success: bool | None
    ledger_success_rate: float
    verified: bool


def run_simulated_cycle(
    state: GameState,
    request: SkillRequest,
    executor: SimulatedSkillExecutor,
    ledger: SkillLedger,
) -> AutonomyCycleResult:
    gateway = SafeSkillGateway(AutonomyLevel.AUTONOMOUS)
    result = gateway.submit(request, state, executor)
    if result.success is None:
        return AutonomyCycleResult(request.skill, result.accepted, result.executed, None, ledger.skills[request.skill].success_rate, ledger.skills[request.skill].verified)
    record = ledger.record_result(request.skill, result.success, request.confidence)
    return AutonomyCycleResult(request.skill, result.accepted, result.executed, result.success, record.success_rate, record.verified)
