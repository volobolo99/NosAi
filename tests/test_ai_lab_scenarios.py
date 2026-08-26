from app.ai_lab.scenarios import default_scenarios, validate_scenarios


def test_default_scenarios_are_valid() -> None:
    scenarios = default_scenarios()
    assert len(scenarios) == 4
    assert validate_scenarios(scenarios) == []


def test_scenarios_have_unique_ids_and_safe_constraints() -> None:
    scenarios = default_scenarios()
    ids = [scenario["scenario_id"] for scenario in scenarios]
    assert len(ids) == len(set(ids))
    for scenario in scenarios:
        forbidden = set(scenario["constraints"]["forbidden_actions"])
        assert forbidden <= set(scenario["available_actions"]) | {"attack"}
