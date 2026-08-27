from app.adapters.nostale import NosTaleAdapter


def test_nostale_adapter_is_observation_only():
    adapter = NosTaleAdapter(lambda: {"character": {"level": 10}})
    observation = adapter.observe()
    assert observation.state["character"]["level"] == 10
    caps = adapter.capabilities()
    assert caps["observe"] is True
    assert caps["act"] is False
    assert caps["trade"] is False
    assert caps["purchase"] is False
