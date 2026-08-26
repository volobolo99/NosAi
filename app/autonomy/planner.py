"""Deterministic, explainable planner for the first NosAi decision baseline."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import uuid

from app.nostale_perception.game_state import GameState
from app.nostale_perception.state_invariants import validate_game_state


class Goal(str, Enum):
    SURVIVE = "survive"
    OBSERVE_AREA = "observe_area"
    MAINTAIN_STATE = "maintain_state"


@dataclass(frozen=True)
class CandidateSkill:
    skill: str
    score: float
    rationale: str
    allowed: bool


@dataclass(frozen=True)
class DecisionTrace:
    trace_id: str
    goal: Goal
    state_revision: int
    state_valid: bool
    candidates: tuple[CandidateSkill, ...]
    selected_skill: str | None
    reason: str


class DeterministicPlanner:
    """Reference planner; no LLM, network, OS input, or game-side effects."""

    def plan(self, state: GameState, goal: Goal) -> DecisionTrace:
        validation = validate_game_state(state)
        trace_id = uuid.uuid4().hex
        if not validation.valid:
            return DecisionTrace(trace_id, goal, state.revision, False, (), None, "invalid GameState; autonomous decision blocked")

        candidates = self._candidates(state, goal)
        allowed = tuple(candidate for candidate in candidates if candidate.allowed)
        selected = max(allowed, key=lambda item: item.score, default=None)
        return DecisionTrace(
            trace_id,
            goal,
            state.revision,
            True,
            tuple(candidates),
            selected.skill if selected else None,
            selected.rationale if selected else "no safe candidate available",
        )

    def _candidates(self, state: GameState, goal: Goal) -> tuple[CandidateSkill, ...]:
        candidates = [
            CandidateSkill("observe_area", 0.60, "safe information-gathering baseline", True),
            CandidateSkill("maintain_state", 0.50, "preserve current state without side effects", True),
        ]
        if goal == Goal.SURVIVE and state.player.hp is not None and state.player.hp_max:
            ratio = state.player.hp / state.player.hp_max
            candidates.append(CandidateSkill("maintain_state", 1.0 + (1.0 - ratio), "health is below maximum; prioritize conservative state maintenance", True))
        return tuple(candidates)
