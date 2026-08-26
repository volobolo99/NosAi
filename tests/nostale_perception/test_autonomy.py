from __future__ import annotations

from app.nostale_perception.autonomy import AutonomyLevel, SafeSkillGateway, SkillRequest
from app.nostale_perception.game_state import GameState


def test_default_gateway_never_executes() -> None:
    gateway = SafeSkillGateway()
    result = gateway.submit(SkillRequest("move_to_target", 0.9, "test"), GameState.empty())
    assert result.accepted is False
    assert result.executed is False
    assert result.success is None


def test_assisted_without_executor_is_still_blocked() -> None:
    gateway = SafeSkillGateway(AutonomyLevel.ASSISTED)
    result = gateway.submit(SkillRequest("move_to_target", 0.9, "test"), GameState.empty())
    assert result.executed is False
