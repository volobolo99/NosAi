from nosai.runtime.adapter import RuntimeCommand
from nosai.runtime.safety_gate import GateDecision, RuntimeSafetyGate, SafetyPolicy


def gate():
    return RuntimeSafetyGate(SafetyPolicy(frozenset({"move", "inspect"})))


def test_kill_switch_denies_even_allowlisted_action():
    result = gate().evaluate(RuntimeCommand("move"), session_active=True, kill_switch_engaged=True)
    assert result.decision is GateDecision.DENY
    assert result.reason == "kill switch engaged"


def test_inactive_session_denies():
    result = gate().evaluate(RuntimeCommand("move"), session_active=False, kill_switch_engaged=False)
    assert result.decision is GateDecision.DENY


def test_non_allowlisted_action_denies():
    result = gate().evaluate(RuntimeCommand("attack"), session_active=True, kill_switch_engaged=False)
    assert result.decision is GateDecision.DENY


def test_allowlisted_sandbox_action_can_pass_policy():
    result = gate().evaluate(RuntimeCommand("inspect"), session_active=True, kill_switch_engaged=False)
    assert result.decision is GateDecision.ALLOW_SANDBOX
