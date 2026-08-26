"""Provider-agnostic AI planner contract. Shadow-only: never executes skills."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.nostale_perception.game_state import GameState
from .planner import CandidateSkill, Goal


@dataclass(frozen=True)
class AIProposal:
    goal: Goal
    skill: str | None
    confidence: float
    rationale: str
    candidates: tuple[CandidateSkill, ...] = ()


class AIPlannerProvider(Protocol):
    def propose(self, state: GameState, goal: Goal) -> AIProposal: ...


class ShadowAIPlanner:
    """Calls a provider for advice only. No Gateway/Executor access is exposed."""

    def __init__(self, provider: AIPlannerProvider) -> None:
        self.provider = provider

    def propose(self, state: GameState, goal: Goal) -> AIProposal:
        proposal = self.provider.propose(state, goal)
        if not 0.0 <= proposal.confidence <= 1.0:
            raise ValueError("AI confidence must be in [0,1]")
        return proposal
