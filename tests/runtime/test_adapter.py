from nosai.runtime.adapter import DryRunRuntimeAdapter, NosTaleRuntimeAdapter, RuntimeCommand


def test_dry_run_maps_and_executes_deterministically():
    adapter = DryRunRuntimeAdapter()
    command = adapter.map_decision("move", {"x": "10", "y": "20"})
    assert command == RuntimeCommand("move", (("x", "10"), ("y", "20")))
    result = adapter.execute(command)
    assert result.accepted is True
    assert result.dry_run is True
    assert result.message == "simulated:move"


def test_dry_run_rejects_empty_action():
    try:
        DryRunRuntimeAdapter().map_decision(" ")
    except ValueError as exc:
        assert "non-empty" in str(exc)
    else:
        raise AssertionError("empty action must fail")


def test_nostale_skeleton_is_hard_locked():
    adapter = NosTaleRuntimeAdapter()
    command = adapter.map_decision("attack", {"target": "dummy"})
    result = adapter.execute(command)
    assert result.accepted is False
    assert result.dry_run is False
    assert "disabled" in result.message
