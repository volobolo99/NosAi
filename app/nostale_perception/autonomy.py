"""Safe autonomy ladder and abstract skill execution boundary."""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Protocol

from .game_state import GameState


class AutonomyLevel(IntEnum):
    OBSERVE = 0
    SHADOW = 1
    ASSISTED = 2
    SUPERVISED = 3
    AUTONOMOUS = 4


@dataclass(frozen=True)
class SkillRequest:
    skill: str
    confidence: float
    reason: str


@dataclass(frozen=True)
class ExecutionResult:
    skill: str
    accepted: bool
    executed: bool
    success: bool | None
    message: str


class SkillExecutor(Protocol):
    def execute(self, request: SkillRequest, state: GameState) -> ExecutionResult: ...


class SafeSkillGateway:
    """Policy gate. Runtime execution remains disabled until an explicit executor is supplied."""

    def __init__(self, level: AutonomyLevel = AutonomyLevel.OBSERVE) -> None:
        self.level = level

    def submit(self, request: SkillRequest, state: GameState, executor: SkillExecutor | None = None) -> ExecutionResult:
        if self.level < AutonomyLevel.ASSISTED:
            return ExecutionResult(request.skill, False, False, None, "autonomy level does not permit execution")
        if executor is None:
            return ExecutionResult(request.skill, False, False, None, "no executor configured")
        return executor.execute(request, state)
