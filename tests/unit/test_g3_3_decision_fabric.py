from app.ai.contracts import ActionIntent, ActionKind, Goal, WorldState
from app.ai.g3_3 import DefaultGuardAi, DecisionFabric, StaticPlayAi


def state() -> WorldState:
    return WorldState(timestamp=123.0)


def goal() -> Goal:
    return Goal(kind="survive", priority=1.0)


def test_approved_proposal_never_crosses_execution_boundary() -> None:
    player = StaticPlayAi(ActionIntent(ActionKind.WAIT), confidence=0.9)
    fabric = DecisionFabric(player)

    result = fabric.decide(state(), goal())

    assert result.approved is True
    assert result.verdict.allowed is True
    assert fabric.can_execute(result) is False


def test_low_confidence_is_rejected() -> None:
    player = StaticPlayAi(ActionIntent(ActionKind.ATTACK), confidence=0.2)
    result = DecisionFabric(player).decide(state(), goal())

    assert result.approved is False
    assert "confidence_below_threshold" in result.verdict.reasons


def test_missing_rationale_is_rejected() -> None:
    player = StaticPlayAi(ActionIntent(ActionKind.MOVE), confidence=0.9, rationale="   ")
    result = DecisionFabric(player).decide(state(), goal())

    assert result.approved is False
    assert "missing_rationale" in result.verdict.reasons


def test_safety_flag_is_required() -> None:
    player = StaticPlayAi(ActionIntent(ActionKind.HEAL), confidence=0.9)
    original = player.propose

    def unsafe_proposal(current_state, current_goal):
        decision = original(current_state, current_goal)
        return decision.__class__(
            selected=decision.selected,
            confidence=decision.confidence,
            rationale=decision.rationale,
            safety_ok=False,
            timestamp=decision.timestamp,
        )

    player.propose = unsafe_proposal  # type: ignore[method-assign]
    result = DecisionFabric(player).decide(state(), goal())

    assert result.approved is False
    assert "safety_flag_not_set" in result.verdict.reasons


def test_guard_rejects_invalid_confidence() -> None:
    player = StaticPlayAi(ActionIntent(ActionKind.WAIT), confidence=1.5)
    result = DecisionFabric(player, DefaultGuardAi()).decide(state(), goal())

    assert result.approved is False
    assert "invalid_confidence" in result.verdict.reasons
