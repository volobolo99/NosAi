"""Canonical deterministic NosTale-like benchmark scenarios.

Scenarios are synthetic but expressed through the same GameState/observation boundary
used by replay ingestion. They are deliberately side-effect free.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable

from app.nostale_perception.game_state import GameState
from app.nostale_perception.network_decoder import DecodedObservation
from .planner import Goal


class ScenarioKind(str, Enum):
    HEALTHY_IDLE = "healthy_idle"
    LOW_HP = "low_hp"
    FULL_HEALTH = "full_health"
    INVALID_STATE = "invalid_state"
    WORLD_ENTITY = "world_entity"


@dataclass(frozen=True)
class NosTaleScenario:
    scenario_id: str
    kind: ScenarioKind
    goal: Goal
    description: str
    build: Callable[[], GameState]


def _state(hp: int, hp_max: int = 100) -> GameState:
    state = GameState.empty()
    state.apply(DecodedObservation("fixture-player", "player_info", {
        "entity_id": 1,
        "hp": hp,
        "hp_max": hp_max,
        "mp": 100,
        "mp_max": 100,
    }, 1.0, "scenario"))
    return state


def _healthy_idle() -> GameState:
    return _state(100)


def _low_hp() -> GameState:
    return _state(20)


def _full_health() -> GameState:
    return _state(100)


def _invalid_state() -> GameState:
    return _state(101)


def _world_entity() -> GameState:
    state = _state(100)
    state.apply(DecodedObservation("fixture-entity", "entity_spawn", {
        "entity_id": 42,
        "kind": "monster",
        "x": 10,
        "y": 12,
    }, 1.0, "scenario"))
    return state


SCENARIOS: tuple[NosTaleScenario, ...] = (
    NosTaleScenario("NT-001", ScenarioKind.HEALTHY_IDLE, Goal.OBSERVE_AREA, "healthy player in a stable observation state", _healthy_idle),
    NosTaleScenario("NT-002", ScenarioKind.LOW_HP, Goal.SURVIVE, "player with critically reduced HP", _low_hp),
    NosTaleScenario("NT-003", ScenarioKind.FULL_HEALTH, Goal.MAINTAIN_STATE, "healthy player maintaining current state", _full_health),
    NosTaleScenario("NT-004", ScenarioKind.INVALID_STATE, Goal.OBSERVE_AREA, "intentionally invalid HP invariant", _invalid_state),
    NosTaleScenario("NT-005", ScenarioKind.WORLD_ENTITY, Goal.OBSERVE_AREA, "player with a world entity observation", _world_entity),
)


def all_scenarios() -> tuple[NosTaleScenario, ...]:
    return SCENARIOS
