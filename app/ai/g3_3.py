"""G3.3 PlayAi/GuardAi decision boundary.

The intelligence layer proposes; the guard validates; the fabric returns a
controlled decision. Nothing in this module executes an action.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.ai.contracts import ActionIntent, Decision, Goal, WorldState

G3_3_VERSION = "3.3"


@dataclass(frozen=True)
class GuardVerdict:
    """Immutable safety result for a proposed decision."""

    allowed: bool
    reasons: tuple[str, ...] = ()
    confidence: float = 0.0
    guard_version: str = G3_3_VERSION


class PlayAi(Protocol):
    """Strategy provider: may propose, but never execute."""

    def propose(self, state: WorldState, goal: Goal) -> Decision: ...


class GuardAi(Protocol):
    """Safety provider that can only accept/reject a proposal."""

    def evaluate(self, state: WorldState, goal: Goal, decision: Decision) -> GuardVerdict: ...


class DefaultGuardAi:
    """Deterministic baseline guard for the G3.3 boundary."""

    def __init__(self, *, min_confidence: float = 0.5) -> None:
        if not 0.0 <= min_confidence <= 1.0:
            raise ValueError("min_confidence must be between 0 and 1")
        self.min_confidence = min_confidence

    def evaluate(self, state: WorldState, goal: Goal, decision: Decision) -> GuardVerdict:
        reasons: list[str] = []
        if decision.contract_version != state.contract_version:
            reasons.append("contract_version_mismatch")
        if not 0.0 <= decision.confidence <= 1.0:
            reasons.append("invalid_confidence")
        if decision.confidence < self.min_confidence:
            reasons.append("confidence_below_threshold")
        if not decision.rationale.strip():
            reasons.append("missing_rationale")
        if decision.selected.kind.value == "noop" and decision.confidence > 0.0:
            # NOOP is valid, but remains explicitly auditable through the rationale.
            pass
        allowed = not reasons and decision.safety_ok
        if not decision.safety_ok and "safety_flag_not_set" not in reasons:
            reasons.append("safety_flag_not_set")
        return GuardVerdict(
            allowed=allowed,
            reasons=tuple(reasons),
            confidence=decision.confidence,
        )


@dataclass(frozen=True)
class FabricResult:
    """Final G3.3 result. `approved` never implies execution."""

    decision: Decision
    verdict: GuardVerdict
    approved: bool


class DecisionFabric:
    """Coordinate PlayAi -> GuardAi without crossing into execution."""

    def __init__(self, player: PlayAi, guard: GuardAi | None = None) -> None:
        self.player = player
        self.guard = guard or DefaultGuardAi()

    def decide(self, state: WorldState, goal: Goal) -> FabricResult:
        decision = self.player.propose(state, goal)
        verdict = self.guard.evaluate(state, goal, decision)
        return FabricResult(decision=decision, verdict=verdict, approved=verdict.allowed)

    def can_execute(self, result: FabricResult) -> bool:
        """Compatibility boundary: execution remains disabled in G3.3."""
        return False


class StaticPlayAi:
    """Small deterministic PlayAi useful for tests, dry-runs and integration wiring."""

    def __init__(self, intent: ActionIntent, *, confidence: float = 0.75, rationale: str = "deterministic proposal") -> None:
        self.intent = intent
        self.confidence = confidence
        self.rationale = rationale

    def propose(self, state: WorldState, goal: Goal) -> Decision:
        return Decision(
            selected=self.intent,
            confidence=self.confidence,
            rationale=self.rationale,
            safety_ok=True,
            timestamp=state.timestamp,
        )
