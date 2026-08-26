"""Replay-to-GameState integration with invariant validation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .game_state import GameState
from .network_decoder import DecodedObservation
from .state_invariants import StateIssue, validate_game_state


@dataclass(frozen=True)
class ReplayStateResult:
    observations: int
    applied: int
    rejected: int
    state: GameState
    issues: tuple[StateIssue, ...]

    @property
    def valid(self) -> bool:
        return not any(issue.severity == "ERROR" for issue in self.issues)


def replay_into_game_state(observations: Iterable[DecodedObservation]) -> ReplayStateResult:
    state = GameState.empty()
    total = applied = 0
    for observation in observations:
        total += 1
        if state.apply(observation):
            applied += 1
    validation = validate_game_state(state)
    return ReplayStateResult(total, applied, total - applied, state, validation.issues)
