import pytest

from nosai.runtime.adapter import RuntimeCommand
from nosai.runtime.sandbox import ControlledSandbox, SessionState


def test_sandbox_lifecycle_and_simulation_are_deterministic():
    sandbox = ControlledSandbox(max_observations=2)
    assert sandbox.state is SessionState.CREATED
    assert sandbox.kill_switch_engaged
    sandbox.start()
    result = sandbox.simulate(RuntimeCommand("move"))
    assert result.accepted and result.dry_run
    assert result.message == "sandbox-simulated:move"
    assert sandbox.observations()[0].event == "simulation"
    sandbox.close()
    assert sandbox.state is SessionState.CLOSED


def test_sandbox_is_bounded():
    sandbox = ControlledSandbox(max_observations=2)
    sandbox.start()
    for action in ("a", "b", "c"):
        sandbox.simulate(RuntimeCommand(action))
    assert [x.action for x in sandbox.observations()] == ["b", "c"]


def test_sandbox_requires_active_session():
    sandbox = ControlledSandbox()
    with pytest.raises(RuntimeError):
        sandbox.simulate(RuntimeCommand("move"))


def test_closed_session_cannot_restart():
    sandbox = ControlledSandbox()
    sandbox.start()
    sandbox.close()
    with pytest.raises(RuntimeError):
        sandbox.start()
