from __future__ import annotations

from typing import Any

SCHEMA_VERSION = 3


def default_scenarios() -> list[dict[str, Any]]:
    return [
        {"scenario_id": "navigation.resistant_target_reposition", "schema_version": SCHEMA_VERSION, "source": "nosai_baseline", "world_state": {"hp_ratio": 0.9, "mp_ratio": 0.8, "target_distance": 12.0, "target_resistance": 1.0, "objective": "target_elimination"}, "available_actions": ["move", "attack", "wait"], "constraints": {"forbidden_actions": [], "preferred_actions": ["move"], "acceptable_actions": ["wait"]}, "expected_decision": "move"},
        {"scenario_id": "navigation.low_mp_stabilize", "schema_version": SCHEMA_VERSION, "source": "nosai_baseline", "world_state": {"hp_ratio": 0.85, "mp_ratio": 0.08, "target_distance": 20.0, "target_resistance": 1.0, "objective": "survival"}, "available_actions": ["move", "wait"], "constraints": {"forbidden_actions": [], "preferred_actions": ["move"], "acceptable_actions": ["wait"]}, "expected_decision": "move"},
        {"scenario_id": "combat.objective_attack", "schema_version": SCHEMA_VERSION, "source": "nosai_baseline", "world_state": {"hp_ratio": 0.9, "mp_ratio": 0.8, "target_distance": 6.0, "target_resistance": 0.2, "time_left_s": 120.0, "objective": "kill_all"}, "available_actions": ["attack", "move", "wait"], "constraints": {"forbidden_actions": [], "preferred_actions": ["attack"], "acceptable_actions": ["move", "wait"]}, "expected_decision": "attack"},
        {"scenario_id": "combat.time_pressure_attack", "schema_version": SCHEMA_VERSION, "source": "nosai_baseline", "world_state": {"hp_ratio": 0.7, "mp_ratio": 0.6, "target_distance": 8.0, "target_resistance": 0.0, "time_left_s": 10.0, "objective": "raid"}, "available_actions": ["attack", "move", "wait"], "constraints": {"forbidden_actions": [], "preferred_actions": ["attack"], "acceptable_actions": ["move"]}, "expected_decision": "attack"},
        {"scenario_id": "combat.critical_hp_retreat", "schema_version": SCHEMA_VERSION, "source": "nosai_baseline", "world_state": {"hp_ratio": 0.12, "mp_ratio": 0.6, "target_distance": 5.0, "target_resistance": 0.0, "objective": "kill_all"}, "available_actions": ["attack", "heal", "retreat", "wait"], "constraints": {"forbidden_actions": ["attack"], "preferred_actions": ["retreat"], "acceptable_actions": ["heal", "wait"]}, "expected_decision": "retreat"},
        {"scenario_id": "combat.last_life_retreat", "schema_version": SCHEMA_VERSION, "source": "nosai_baseline", "world_state": {"hp_ratio": 0.5, "mp_ratio": 0.5, "target_distance": 5.0, "target_resistance": 0.0, "raid_lives": 1, "objective": "raid"}, "available_actions": ["attack", "retreat", "wait"], "constraints": {"forbidden_actions": ["attack"], "preferred_actions": ["retreat"], "acceptable_actions": ["wait"]}, "expected_decision": "retreat"},
        {"scenario_id": "combat.unknown_target_wait", "schema_version": SCHEMA_VERSION, "source": "nosai_baseline", "world_state": {"hp_ratio": 0.65, "mp_ratio": 0.5, "target_distance": 999.0, "target_resistance": 0.0, "objective": "unknown"}, "available_actions": ["wait"], "constraints": {"forbidden_actions": ["attack", "move"], "preferred_actions": ["wait"], "acceptable_actions": []}, "expected_decision": "wait"},
        {"scenario_id": "navigation.forced_safe_fallback", "schema_version": SCHEMA_VERSION, "source": "nosai_baseline", "world_state": {"hp_ratio": 0.8, "mp_ratio": 0.8, "target_distance": 999.0, "target_resistance": 0.0, "objective": "unknown"}, "available_actions": ["wait"], "constraints": {"forbidden_actions": [], "preferred_actions": ["wait"], "acceptable_actions": []}, "expected_decision": "wait"},
    ]


def validate_scenarios(scenarios: list[dict[str, Any]]) -> list[str]:
    from .evaluator import validate_scenario
    errors: list[str] = []
    for scenario in scenarios:
        errors.extend(f"{scenario.get('scenario_id', '<unknown>')}:{item}" for item in validate_scenario(scenario))
    return errors
