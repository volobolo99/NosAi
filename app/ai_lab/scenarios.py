from __future__ import annotations

from typing import Any

SCHEMA_VERSION = 1


def default_scenarios() -> list[dict[str, Any]]:
    return [
        {
            "scenario_id": "navigation.safe_move",
            "schema_version": SCHEMA_VERSION,
            "source": "nosai_baseline",
            "world_state": {"position_known": True, "path_clear": True, "combat": False},
            "available_actions": ["move", "wait"],
            "constraints": {"forbidden_actions": []},
            "expected_decision": "move",
        },
        {
            "scenario_id": "navigation.unknown_position",
            "schema_version": SCHEMA_VERSION,
            "source": "nosai_baseline",
            "world_state": {"position_known": False, "path_clear": False, "combat": False},
            "available_actions": ["wait"],
            "constraints": {"forbidden_actions": ["move", "attack"]},
            "expected_decision": "wait",
        },
        {
            "scenario_id": "combat.safe_wait",
            "schema_version": SCHEMA_VERSION,
            "source": "nosai_baseline",
            "world_state": {"position_known": True, "target_visible": True, "hp_ratio": 0.12},
            "available_actions": ["wait", "retreat"],
            "constraints": {"forbidden_actions": ["attack"]},
            "expected_decision": "retreat",
        },
        {
            "scenario_id": "combat.unknown_target",
            "schema_version": SCHEMA_VERSION,
            "source": "nosai_baseline",
            "world_state": {"position_known": True, "target_visible": False, "hp_ratio": 0.65},
            "available_actions": ["wait", "move"],
            "constraints": {"forbidden_actions": ["attack"]},
            "expected_decision": "wait",
        },
    ]


def validate_scenarios(scenarios: list[dict[str, Any]]) -> list[str]:
    from .evaluator import validate_scenario

    errors: list[str] = []
    for scenario in scenarios:
        errors.extend(f"{scenario.get('scenario_id', '<unknown>')}:{item}" for item in validate_scenario(scenario))
    return errors
