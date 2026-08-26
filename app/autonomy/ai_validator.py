"""Safety validation for AI proposals before they enter shadow evaluation."""
from __future__ import annotations

from dataclasses import dataclass

from app.nostale_perception.game_state import GameState
from app.nostale_perception.state_invariants import validate_game_state
from .ai_planner import AIProposal
from .planner import CandidateSkill


@dataclass(frozen=True)
class AIValidation:
    valid: bool
    skill_allowed: bool
    reason: str


class AIProposalValidator:
    def validate(self, state: GameState, proposal: AIProposal) -> AIValidation:
        state_validation = validate_game_state(state)
        if not state_validation.valid:
            return AIValidation(False, False, "invalid GameState")
        if proposal.skill is None:
            return AIValidation(True, False, "AI proposed no skill")
        if not proposal.rationale.strip():
            return AIValidation(False, False, "AI rationale is empty")
        if not 0.0 <= proposal.confidence <= 1.0:
            return AIValidation(False, False, "AI confidence out of range")
        candidates = {candidate.skill: candidate for candidate in proposal.candidates}
        candidate = candidates.get(proposal.skill)
        if candidate is None:
            return AIValidation(False, False, "proposed skill is not in AI candidate set")
        if not candidate.allowed:
            return AIValidation(True, False, "proposed skill is explicitly disallowed")
        return AIValidation(True, True, "proposal is structurally valid and candidate is allowed")
