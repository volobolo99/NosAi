from app.ai_lab.evidence import baseline_evidence, scenario_evidence
from app.ai_lab.runner import run_baseline


def test_scenario_evidence_contains_runner_and_oracle_fields() -> None:
    evidence = scenario_evidence(run_baseline()[0])
    assert evidence["scenario_id"]
    assert "decision" in evidence
    assert "confidence" in evidence
    assert "evaluation_status" in evidence
    assert "safety_status" in evidence
    assert "oracle_status" in evidence
    assert isinstance(evidence["reason_codes"], list)
    assert isinstance(evidence["world_state"], dict)


def test_baseline_evidence_is_one_record_per_scenario() -> None:
    runs = run_baseline()
    evidence = baseline_evidence(runs)
    assert len(evidence) == len(runs)
    assert [item["scenario_id"] for item in evidence] == [run.result.scenario_id for run in runs]
