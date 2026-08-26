"""Deterministic recovery policy for failed or blocked decision cycles."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .planner import CandidateSkill, DecisionTrace, Goal


class RecoveryAction(str, Enum):
    RETRY = "retry"
    ALTERNATIVE = "alternative"
    SAFE_FALLBACK = "safe_fallback"
    ABORT = "abort"


@dataclass(frozen=True)
class RecoveryDecision:
    action: RecoveryAction
    skill: str | None
    attempt: int
    reason: str


class RecoveryManager:
    """Chooses recovery without performing any game-side action."""

    def __init__(self, max_retries: int = 1) -> None:
        if max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        self.max_retries = max_retries

    def decide(
        self,
        trace: DecisionTrace,
        *,
        attempt: int,
        outcome: str,
        candidates: Iterable[CandidateSkill] | None = None,
    ) -> RecoveryDecision:
        if not trace.state_valid:
            return RecoveryDecision(RecoveryAction.ABORT, None, attempt, "invalid GameState")
        if outcome in {"success"}:
            return RecoveryDecision(RecoveryAction.ABORT, None, attempt, "no recovery required")
        if outcome in {"execution_blocked", "decision_blocked"}:
            return RecoveryDecision(RecoveryAction.SAFE_FALLBACK, "maintain_state", attempt, "execution path blocked; use conservative fallback")
        if outcome == "execution_failed" and attempt < self.max_retries:
            return RecoveryDecision(RecoveryAction.RETRY, trace.selected_skill, attempt + 1, "retry budget available")
        alternatives = [c for c in (candidates or trace.candidates) if c.allowed and c.skill != trace.selected_skill]
        if alternatives:
            alternative = max(alternatives, key=lambda c: c.score)
            return RecoveryDecision(RecoveryAction.ALTERNATIVE, alternative.skill, attempt, "primary skill failed; select highest-scoring safe alternative")
        return RecoveryDecision(RecoveryAction.SAFE_FALLBACK, "maintain_state", attempt, "no safe alternative available")
