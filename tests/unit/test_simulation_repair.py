from app.simulation_repair import CandidateResult, ErrorEvent, SimulationRepairEngine


def test_error_fingerprint_is_stable() -> None:
    event = ErrorEvent.create(
        source="CI", severity="ERROR", component="client", test_name="connection", error_type="TimeoutError", message="timeout"
    )
    first = SimulationRepairEngine.fingerprint(event)
    second = SimulationRepairEngine.fingerprint(event)
    assert first == second


def test_pipeline_never_applies_candidate_automatically() -> None:
    event = ErrorEvent.create(
        source="REAL", severity="ERROR", component="runtime", test_name="probe", error_type="ValueError", message="bad state"
    )
    engine = SimulationRepairEngine()
    run = engine.register_error(event)
    engine.research(run.run_id, event)
    result = engine.evaluate(run.run_id, event, [CandidateResult(candidate_id="C1", status="QUEUED", description="candidate")])
    assert result.candidates[0].status == "NOT_RUN"
    assert result.sealed is False


def test_sealed_report_requires_explicit_seal(tmp_path) -> None:
    event = ErrorEvent.create(
        source="SIMULATED", severity="ERROR", component="test", test_name="x", error_type="AssertionError", message="x"
    )
    engine = SimulationRepairEngine()
    run = engine.register_error(event)
    try:
        from app.simulation_repair.report import seal_report
        seal_report(run, tmp_path)
    except ValueError:
        pass
    else:
        raise AssertionError("unsealed simulation must not be exported")
