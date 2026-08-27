import pytest

from nosai.runtime.recovery import RuntimeRecovery, SessionState
from nosai.runtime.session_manager import RuntimeSessionManager, SessionEvent


def test_session_lifecycle_and_heartbeat():
    manager = RuntimeSessionManager(RuntimeRecovery(), timeout_seconds=10)
    snapshot = manager.start("s-13")
    assert snapshot.state is SessionState.ACTIVE
    assert snapshot.kill_switch_engaged
    manager.heartbeat(now=100.0)
    assert manager.check_timeout(now=109.9).state is SessionState.ACTIVE
    assert manager.events() == (SessionEvent.STARTED, SessionEvent.HEARTBEAT)


def test_timeout_fails_closed():
    manager = RuntimeSessionManager(RuntimeRecovery(), timeout_seconds=10)
    manager.start("s-13")
    manager.heartbeat(now=100.0)
    snapshot = manager.check_timeout(now=110.1)
    assert snapshot.state is SessionState.DEGRADED
    assert snapshot.kill_switch_engaged
    assert SessionEvent.TIMEOUT in manager.events()


def test_invalid_session_and_duplicate_start_are_rejected():
    manager = RuntimeSessionManager(RuntimeRecovery())
    with pytest.raises(ValueError):
        manager.start("")
    manager.start("s-13")
    with pytest.raises(RuntimeError):
        manager.start("s-14")


def test_close_is_safe_and_idempotent():
    manager = RuntimeSessionManager(RuntimeRecovery())
    manager.start("s-13")
    assert manager.close().state is SessionState.CLOSED
    assert manager.close().state is SessionState.CLOSED
