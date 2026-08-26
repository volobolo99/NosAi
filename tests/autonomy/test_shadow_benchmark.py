from __future__ import annotations

from app.autonomy.ai_planner import AIProposal, ShadowAIPlanner
from app.autonomy.planner import CandidateSkill, Goal
from app.autonomy.shadow_benchmark import ShadowBenchmark
from app.nostale_perception.game_state import GameState
from app.nostale_perception.network_decoder import DecodedObservation


class FakeProvider:
    def propose(self, state: GameState, goal: Goal) -> AIProposal:
        return AIProposal(
            goal,
            "observe_area",
            0.9,
            "safe observation",
            (CandidateSkill("observe_area", 0.9, "safe", True),),
        )


def test_shadow_benchmark_reports_multiple_episodes() -> None:
    state = GameState.empty()
    state.apply(DecodedObservation("p", "player_info", {"entity_id": 1, "hp": 100, "hp_max": 100}, 0.9, "fixture"))
    report = ShadowBenchmark(ShadowAIPlanner(FakeProvider())).run([
        (state, Goal.OBSERVE_AREA),
        (state, Goal.OBSERVE_AREA),
    ])
    assert report.episodes == 2
    assert report.agreements == 2
    assert report.valid_ai == 2
    assert report.allowed_ai == 2
    assert report.agreement_rate == 1.0
    assert report.baseline_success_rate == 1.0
