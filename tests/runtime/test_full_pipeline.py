from nosai.runtime.adapter import DryRunRuntimeAdapter, NosTaleRuntimeAdapter


def test_full_pipeline_simulation_boundary():
    """Exercise the G3.3->G3.4 boundary without real runtime side effects."""
    # A DecisionFabric-produced action is represented here as a canonical action
    # because this test intentionally remains independent of concrete providers.
    action = "move"
    parameters = {"x": "10", "y": "20"}

    dry = DryRunRuntimeAdapter()
    command = dry.map_decision(action, parameters)
    result = dry.execute(command)

    assert result.accepted
    assert result.dry_run
    assert result.message == "simulated:move"

    # The real NosTale boundary remains fail-closed.
    nostale = NosTaleRuntimeAdapter()
    locked = nostale.execute(nostale.map_decision(action, parameters))
    assert not locked.accepted
    assert "disabled" in locked.message
