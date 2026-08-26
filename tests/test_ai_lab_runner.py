from app.ai_lab.runner import run_baseline


def test_baseline_runs_against_real_brain_without_client_side_effects() -> None:
    runs = run_baseline()
    assert len(runs) == 4
    assert all(run.result.decision is not None for run in runs)
    assert all(run.result.safety_status == "PASS" for run in runs)


def test_baseline_produces_reproducible_scenario_ids() -> None:
    first = [run.result.scenario_id for run in run_baseline()]
    second = [run.result.scenario_id for run in run_baseline()]
    assert first == second
