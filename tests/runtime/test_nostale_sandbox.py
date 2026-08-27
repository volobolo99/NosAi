from nosai.runtime.adapter import RuntimeCommand
from nosai.runtime.nostale_sandbox import NosTaleSandboxAdapter, RuntimeStatus


def test_discovery_is_non_invasive_and_observation_only():
    adapter = NosTaleSandboxAdapter()
    initial = adapter.discover()
    assert initial.status is RuntimeStatus.UNKNOWN
    assert "observation_only" in initial.capabilities
    assert adapter.real_execution_enabled is False

    observed = adapter.discover(observed=True, version="sandbox")
    assert observed.status is RuntimeStatus.AVAILABLE
    assert observed.product == "NosTale"
    assert adapter.real_execution_enabled is False


def test_simulation_requires_discovery():
    adapter = NosTaleSandboxAdapter()
    command = RuntimeCommand("move")
    assert adapter.simulate(command).accepted is False
    adapter.discover(observed=True)
    result = adapter.simulate(command)
    assert result.accepted is True
    assert result.dry_run is True


def test_real_execution_is_hard_locked():
    adapter = NosTaleSandboxAdapter()
    result = adapter.execute(RuntimeCommand("attack"))
    assert result.accepted is False
    assert result.dry_run is False
    assert "disabled" in result.message
