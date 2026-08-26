from __future__ import annotations

from app.autonomy.ai_planner import AIProposal, ShadowAIPlanner
from app.autonomy.ai_validator import AIProposalValidator
from app.autonomy.planner import CandidateSkill, DeterministicPlanner, Goal
from app.autonomy.shadow_compare import ShadowComparator
from app.autonomy.shadow_ledger import ShadowLedger
from app.nostale_perception.game_state import GameState
from app.nostale_perception.network_decoder import DecodedObservation


class FakeProvider:
    def __init__(self, proposal: AIProposal) -> None:
        self.proposal = proposal

    def propose(self, state: GameState, goal: Goal) -> AIProposal:
        return self.proposal


def _state() -> GameState:
    state = GameState.empty()
    state.apply(DecodedObservation("p", "player_info", {"entity_id": 1, "hp": 100, "hp_max": 100}, 0.9, "fixture"))
    return state


def test_shadow_comparator_records_agreement_without_execution() -> None:
    proposal = AIProposal(Goal.OBSERVE_AREA, "observe_area", 0.92, "safe observation", (CandidateSkill("observe_area", 0.9, "safe", True),))
    ledger = ShadowLedger()
    comparison = ShadowComparator(ShadowAIPlanner(FakeProvider(proposal)), ledger).compare(_state(), Goal.OBSERVE_AREA)
    assert comparison.record.agreement is True
    assert comparison.record.ai_valid is True
    assert comparison.record.ai_allowed is True
    assert ledger.count == 1
    assert ledger.agreement_rate() == 1.0


def test_validator_rejects_skill_not_in_candidate_set() -> None:
    proposal = AIProposal(Goal.OBSERVE_AREA, "attack", 0.9, "attack", ())
    validation = AIProposalValidator().validate(_state(), proposal)
    assert validation.valid is False
    assert validation.skill_allowed is False


def test_shadow_ai_cannot_execute() -> None:
    proposal = AIProposal(Goal.OBSERVE_AREA, "observe_area", 0.9, "safe", (CandidateSkill("observe_area", 0.9, "safe", True),))
    planner = ShadowAIPlanner(FakeProvider(proposal))
    result = planner.propose(_state(), Goal.OBSERVE_AREA)
    assert result.skill == "observe_area"
    # Contract intentionally exposes no gateway/executor method.
    assert not hasattr(planner, "executor")
