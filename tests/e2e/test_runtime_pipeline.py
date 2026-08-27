"""G3.12 end-to-end certification of the controlled runtime pipeline."""
from nosai.runtime.adapter import RuntimeCommand
from nosai.runtime.nostale_sandbox import NosTaleSandboxAdapter
from nosai.runtime.orchestrator import RuntimeOrchestrator
from nosai.runtime.recovery import RuntimeRecovery, SessionState
from nosai.runtime.safety_gate import RuntimeSafetyGate, SafetyPolicy
from nosai.runtime.telemetry import TelemetryCollector


def build_pipeline():
    return RuntimeOrchestrator(
        RuntimeSafetyGate(SafetyPolicy(frozenset({"inspect", "move"}))),
        NosTaleSandboxAdapter(),
        RuntimeRecovery(),
        TelemetryCollector(),
    )


def test_authorized_command_flows_through_entire_sandbox_pipeline():
    pipeline = build_pipeline()
    pipeline.start()
    result = pipeline.command(RuntimeCommand("inspect"))
    assert result.result.accepted is True
    assert result.result.dry_run is True
    assert pipeline._recovery.state is SessionState.ACTIVE
    assert pipeline._telemetry.counts()["command"] == 1


def test_unsafe_command_is_denied_without_real_execution():
    pipeline = build_pipeline()
    pipeline.start()
    result = pipeline.command(RuntimeCommand("attack"))
    assert result.result.accepted is False
    assert result.result.dry_run is True
    assert result.reason == "action not allowlisted"


def test_fault_recovery_and_close_are_observable_end_to_end():
    pipeline = build_pipeline()
    pipeline.start()
    pipeline.fault_and_recover("sandbox disconnect")
    assert pipeline._recovery.state is SessionState.SAFE
    pipeline.close()
    assert pipeline._recovery.state is SessionState.CLOSED
    assert pipeline._telemetry.counts()["recovery"] == 2


def test_execution_lock_is_preserved_by_pipeline_components():
    pipeline = build_pipeline()
    pipeline.start()
    assert pipeline._sandbox.real_execution_enabled is False
    assert pipeline._recovery.kill_switch_engaged is True
