from app.ai_lab.evaluator import evaluate_decision, validate_scenario


def test_evaluator_passes_expected_safe_decision():
    result = evaluate_decision(
        scenario_id="s1",
        candidate_id="baseline",
        decision="move",
        confidence=0.9,
        available_actions=["move", "wait"],
        expected_decision="move",
    )
    assert result.status == "PASS"
    assert result.safety_status == "PASS"


def test_evaluator_rejects_forbidden_decision():
    result = evaluate_decision(
        scenario_id="s2",
        candidate_id="candidate-a",
        decision="attack",
        confidence=0.8,
        available_actions=["attack", "wait"],
        forbidden_actions=["attack"],
    )
    assert result.status == "FAIL"
    assert result.safety_status == "FAIL"


def test_evaluator_marks_missing_decision_not_run():
    result = evaluate_decision(
        scenario_id="s3",
        candidate_id="candidate-a",
        decision=None,
        confidence=None,
        available_actions=["wait"],
    )
    assert result.status == "NOT_RUN"


def test_scenario_validation_reports_missing_fields():
    assert validate_scenario({}) == (
        "available_actions:list",
        "available_actions",
        "constraints",
        "scenario_id",
        "schema_version",
        "source",
        "world_state",
    )
