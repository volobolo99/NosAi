"""Shadow-mode evaluation: produce intended outcomes without executing game actions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .game_state import GameState


@dataclass(frozen=True)
class ShadowDecision:
    skill: str
    confidence: float
    rationale: str
    executed: bool = False


class ShadowExecutor:
    def __init__(self, policy: Callable[[GameState], ShadowDecision]) -> None:
        self.policy = policy

    def evaluate(self, state: GameState) -> ShadowDecision:
        decision = self.policy(state)
        if decision.executed:
            raise ValueError("shadow mode cannot execute actions")
        return decision
