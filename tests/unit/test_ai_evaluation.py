from app.ai.evaluation import EvaluationCase, EvaluationRunner, summarize


def provider(state, objective):
    return {
        "action_type": state["expected_action"],
        "valid": state.get("valid", True),
        "fallback_used": state.get("fallback", False),
    }


def test_evaluation_covers_valid_and_invalid_cases():
    cases = [
        EvaluationCase("combat-001", "combat", {"expected_action": "attack"}, "fight", "attack"),
        EvaluationCase("invalid-001", "invalid_state", {"expected_action": "none", "valid": False}, "recover", "none", False),
    ]
    results = EvaluationRunner(provider).run(cases)
    assert all(result.passed for result in results)
    assert summarize(results)["pass_rate"] == 1.0


def test_fallback_rate_is_reported():
    cases = [
        EvaluationCase("recovery-001", "recovery", {"expected_action": "recover", "fallback": True}, "recover", "recover"),
        EvaluationCase("navigation-001", "navigation", {"expected_action": "move"}, "travel", "move"),
    ]
    results = EvaluationRunner(provider).run(cases)
    assert summarize(results)["fallback_rate"] == 0.5


def test_provider_failure_is_reported_without_aborting_suite():
    def broken_provider(state, objective):
        raise RuntimeError("mock provider failure")

    cases = [EvaluationCase("failure-001", "ambiguous", {}, "decide", "attack", False)]
    result = EvaluationRunner(broken_provider).run(cases)[0]
    assert result.passed
    assert result.error == "RuntimeError: mock provider failure"
