from nosai.runtime.adapter import RuntimeCommand
from nosai.runtime.orchestrator import RuntimeOrchestrator
from nosai.runtime.nostale_sandbox import NosTaleSandboxAdapter
from nosai.runtime.recovery import RuntimeRecovery
from nosai.runtime.safety_gate import RuntimeSafetyGate, SafetyPolicy
from nosai.runtime.telemetry import TelemetryCollector


def make_orchestrator():
    gate = RuntimeSafetyGate(SafetyPolicy(frozenset({"move", "inspect"})))
    return RuntimeOrchestrator(gate, NosTaleSandboxAdapter(), RuntimeRecovery(), TelemetryCollector())


def test_orchestrator_composes_full_sandbox_pipeline():
    orchestrator = make_orchestrator()
    orchestrator.start()
    result = orchestrator.command(RuntimeCommand("inspect"))
    assert result.result.accepted
    assert result.result.dry_run
    orchestrator.fault_and_recover("disconnect")
    orchestrator.close()


def test_orchestrator_denies_unsafe_action():
    orchestrator = make_orchestrator()
    orchestrator.start()
    result = orchestrator.command(RuntimeCommand("attack"))
    assert not result.result.accepted
    assert result.result.dry_run
