from app.nostale.strategy import (
    HardcoreRaidState,
    NosTaleState,
    RoomObjective,
    assess_strategy,
    build_reward_context,
)


def test_resistance_threshold_becomes_explicit_priority():
    state = NosTaleState(target_resist_net=1.05)
    assessment = assess_strategy(state)
    assert assessment.resistance_break_critical is True
    assert assessment.recommended_focus == "break_resistance_threshold"
    assert assessment.reward_adjustments["resistance_threshold"] == 10.0


def test_dignity_guard_activates_below_source_boundary():
    assessment = assess_strategy(NosTaleState(dignity=-401))
    assert assessment.dignity_guard is True


def test_room_objective_overrides_generic_focus():
    state = NosTaleState(room_objective=RoomObjective.TARGET_ELIMINATION, target_resist_net=1.5)
    assert assess_strategy(state).recommended_focus == "primary_target_burst"


def test_hardcore_life_pool_increases_risk_signal():
    state = NosTaleState(hardcore=HardcoreRaidState(team_lives_pool=2))
    context = build_reward_context(state)
    assert context.risk == 2.0
    assert context.metadata["source_basis"] == "Guida Strategica e Analisi NosTale.pdf"


def test_state_rejects_invalid_dignity():
    try:
        NosTaleState(dignity=-1001)
    except ValueError as exc:
        assert "dignity" in str(exc)
    else:
        raise AssertionError("invalid dignity must be rejected")
