import pytest

from nosai.runtime.recovery import RuntimeRecovery, SessionState


def test_fault_recover_ends_in_safe_state():
    recovery = RuntimeRecovery()
    recovery.start()
    recovery.fault("disconnect")
    assert recovery.state is SessionState.DEGRADED
    recovery.recover()
    assert recovery.state is SessionState.SAFE
    assert recovery.kill_switch_engaged
    assert [event.state for event in recovery.events()] == [SessionState.ACTIVE, SessionState.DEGRADED, SessionState.RECOVERING, SessionState.SAFE]


def test_recovery_requires_fault():
    recovery = RuntimeRecovery()
    recovery.start()
    with pytest.raises(RuntimeError):
        recovery.recover()


def test_fault_reason_is_required():
    recovery = RuntimeRecovery()
    with pytest.raises(ValueError):
        recovery.fault("")


def test_close_is_terminal():
    recovery = RuntimeRecovery()
    recovery.start()
    recovery.close()
    assert recovery.state is SessionState.CLOSED
    recovery.close()
    assert recovery.state is SessionState.CLOSED
