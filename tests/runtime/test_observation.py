from nosai.runtime.observation import KillSwitch, ObservationBuffer


def test_observation_buffer_is_bounded_and_deterministic():
    buffer = ObservationBuffer(max_items=2)
    buffer.record("state", {"hp": "100"})
    buffer.record("state", {"hp": "90"})
    buffer.record("state", {"hp": "80"})
    snapshot = buffer.snapshot()
    assert len(snapshot) == 2
    assert snapshot[0].payload == (("hp", "90"),)
    assert snapshot[1].payload == (("hp", "80"),)


def test_observation_rejects_empty_kind():
    buffer = ObservationBuffer()
    try:
        buffer.record(" ")
    except ValueError:
        pass
    else:
        raise AssertionError("empty observation kind must fail")


def test_kill_switch_is_engaged_and_never_allows_execution():
    switch = KillSwitch()
    assert switch.engaged
    assert not switch.allows_execution()
    switch.release()
    assert switch.engaged
    assert not switch.allows_execution()
