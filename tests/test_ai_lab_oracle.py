from app.ai_lab.oracle import evaluate_oracle


def test_critical_hp_is_safety_critical():
    result = evaluate_oracle(world_state={"hp_ratio": 0.10}, decision="attack", available_actions=["attack", "retreat"])
    assert result.safety_status == "PASS"
    assert result.status == "FAIL"
    assert "CRITICAL_HP_PRIORITY" in result.reason_codes


def test_safe_alternative_is_not_strategic_failure():
    result = evaluate_oracle(world_state={"hp_ratio": 0.80}, decision="wait", available_actions=["attack", "wait"], preferred_actions=["attack"], acceptable_actions=["wait"])
    assert result.status == "PASS"


def test_different_but_safe_decision_is_distinguished():
    result = evaluate_oracle(world_state={"hp_ratio": 0.80}, decision="wait", available_actions=["attack", "wait"], preferred_actions=["attack"])
    assert result.status == "SAFE-BUT-DIFFERENT"
