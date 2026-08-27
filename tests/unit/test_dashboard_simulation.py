from app.dashboard.server import simulation_data


def test_simulation_dashboard_contract() -> None:
    payload = simulation_data()
    assert set(payload) == {"runs", "latest", "count"}
    assert isinstance(payload["runs"], list)
    assert isinstance(payload["count"], int)
