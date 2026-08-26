from __future__ import annotations

from app.nostale_perception.evaluation_harness import evaluate_shadow_cases
from app.nostale_perception.game_state import GameState
from app.nostale_perception.shadow_mode import ShadowDecision


def test_shadow_mode_never_executes() -> None:
    state = GameState.empty()

    def policy(_state: GameState) -> ShadowDecision:
        return ShadowDecision("observe", 0.9, "test")

    summary = evaluate_shadow_cases([(state, True)], policy)
    assert summary.cases == 1
    assert summary.success_rate == 1.0
    assert summary.intervention_rate == 0.0
