from app.zmsia.core import (
    Decision,
    MockDecisionProvider,
    Plan,
    SafetyDecision,
    State,
)


def test_contracts_are_immutable_and_provider_neutral():
    state = State(state_id="s1", timestamp_ms=1, values={"ready": True})
    plan = Plan(plan_id="p1", goal_id="g1", steps=("noop",))

    decision = MockDecisionProvider().decide(state=state, plan=plan)

    assert isinstance(decision, Decision)
    assert decision.provider == "mock"
    assert decision.plan_id == "p1"
    assert decision.action_id == "noop"

    try:
        state.state_id = "changed"  # type: ignore[misc]
    except (AttributeError, TypeError):
        pass
    else:
        raise AssertionError("Core contracts must be immutable")


def test_safety_decision_is_explicit():
    gate = SafetyDecision(
        allowed=False,
        reason="live mode disabled in test",
        policy_version="test-1",
    )

    assert gate.allowed is False
    assert gate.policy_version == "test-1"
