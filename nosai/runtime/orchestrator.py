"""G3.11 controlled runtime integration orchestrator."""
from __future__ import annotations

from dataclasses import dataclass

from .adapter import RuntimeCommand, RuntimeResult
from .safety_gate import GateDecision, RuntimeSafetyGate
from .nostale_sandbox import NosTaleSandboxAdapter
from .recovery import RuntimeRecovery, SessionState
from .telemetry import TelemetryCollector


@dataclass(frozen=True)
class OrchestrationResult:
    result: RuntimeResult
    reason: str


class RuntimeOrchestrator:
    """Composes safety, state, sandbox and telemetry without real execution."""

    def __init__(self, safety_gate: RuntimeSafetyGate, sandbox: NosTaleSandboxAdapter,
                 recovery: RuntimeRecovery, telemetry: TelemetryCollector) -> None:
        self._gate = safety_gate
        self._sandbox = sandbox
        self._recovery = recovery
        self._telemetry = telemetry

    def start(self) -> None:
        self._recovery.start()
        self._sandbox.discover(observed=True, version="sandbox")
        self._telemetry.record("sandbox", "session", "start", "active")

    def command(self, command: RuntimeCommand) -> OrchestrationResult:
        if self._recovery.state is not SessionState.ACTIVE:
            result = RuntimeResult(False, True, "session not active")
            self._telemetry.record("sandbox", "command", command.action, "denied-state")
            return OrchestrationResult(result, "state boundary")
        evaluation = self._gate.evaluate(command, session_active=True, kill_switch_engaged=False)
        if evaluation.decision is not GateDecision.ALLOW_SANDBOX:
            result = RuntimeResult(False, True, evaluation.reason)
            self._telemetry.record("sandbox", "command", command.action, "denied-policy")
            return OrchestrationResult(result, evaluation.reason)
        result = self._sandbox.simulate(command)
        self._telemetry.record("sandbox", "command", command.action, "simulated")
        return OrchestrationResult(result, "sandbox policy satisfied")

    def fault_and_recover(self, reason: str) -> None:
        self._recovery.fault(reason)
        self._telemetry.record("sandbox", "recovery", "fault", "degraded")
        self._recovery.recover()
        self._telemetry.record("sandbox", "recovery", "recover", "safe")

    def close(self) -> None:
        self._recovery.close()
        self._telemetry.record("sandbox", "session", "close", "closed")
