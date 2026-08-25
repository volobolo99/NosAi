from app.m15.release_gate import ReliabilityGate


def test_long_run_executes_requested_iterations():
    calls = {"n": 0}
    report = ReliabilityGate().execute_long_run(lambda: calls.__setitem__("n", calls["n"] + 1), 25)
    assert report.passed and calls["n"] == 25 and report.iterations == 25


def test_fault_injection_requires_expected_exception():
    report = ReliabilityGate().execute_fault_injection(lambda: (_ for _ in ()).throw(ValueError()), ValueError)
    assert report.passed
    assert not ReliabilityGate().execute_fault_injection(lambda: None, ValueError).passed


def test_recovery_requires_failure_and_validated_recovery():
    state = {"value": 0}

    def fail():
        state["value"] = 99
        raise RuntimeError("boom")

    def recover():
        state["value"] = 0
        return state["value"] == 0

    report = ReliabilityGate().execute_recovery(fail, recover, validator=lambda value: value is True)
    assert report.passed and state["value"] == 0


def test_reproducibility_uses_hashes():
    report = ReliabilityGate().execute_reproducibility(lambda: {"b": 2, "a": 1}, 3)
    assert report.passed and report.digest_before == report.digest_after


def test_hardened_suite_runs_real_sandbox():
    result = ReliabilityGate().hardened_suite(iterations=250)
    assert result["long_run"]["passed"]
    assert result["fault_injection"]["passed"]
    assert result["recovery"]["passed"]
    assert result["reproducibility"]["passed"]
    assert result["end_to_end"]["passed"]
