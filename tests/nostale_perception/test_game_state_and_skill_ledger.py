from __future__ import annotations

from app.nostale_perception.game_state import GameState
from app.nostale_perception.network_decoder import DecodedObservation
from app.nostale_perception.skill_ledger import SkillLedger, SkillRecord


def test_unified_game_state_routes_player_and_world() -> None:
    state = GameState.empty()
    assert state.apply(DecodedObservation("p1", "player_info", {"entity_id": 42, "hp": 90, "hp_max": 100, "mp": 30, "mp_max": 50}, 0.9, "test"))
    assert state.apply(DecodedObservation("m1", "movement", {"entity_id": 7, "x": 10.0, "y": 20.0}, 0.8, "test"))
    assert state.player.entity_id == 42
    assert state.world.entities[7].x == 10.0
    assert state.revision == 2


def test_skill_ledger_requires_repeated_verified_success() -> None:
    ledger = SkillLedger()
    ledger.upsert(SkillRecord("move_to_target", "1"))
    for _ in range(3):
        ledger.record_result("move_to_target", True, 0.9)
    assert ledger.skills["move_to_target"].verified
