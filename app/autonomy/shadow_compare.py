"""Deterministic-vs-AI shadow comparison without execution authority."""
from __future__ import annotations

from dataclasses import dataclass

from app.nostale_perception.game_state import GameState
from .ai_planner import ShadowAIPlanner
from .ai_validator import AIProposalValidator
from .planner import DeterministicPlanner, Goal, DecisionTrace
from .shadow_ledger import ShadowLedger, ShadowRecord


@dataclass(frozen=True)
class ShadowComparison:
    deterministic: DecisionTrace
    record: ShadowRecord


class ShadowComparator:
    def __init__(self, ai_planner: ShadowAIPlanner, ledger: ShadowLedger | None = None) -> None:
        self.deterministic = DeterministicPlanner()
        self.ai_planner = ai_planner
        self.validator = AIProposalValidator()
        self.ledger = ledger or ShadowLedger()

    def compare(self, state: GameState, goal: Goal) -> ShadowComparison:
        trace = self.deterministic.plan(state, goal)
        proposal = self.ai_planner.propose(state, goal)
        validation = self.validator.validate(state, proposal)
        record = self.ledger.record(trace, proposal, validation)
        return ShadowComparison(trace, record)
