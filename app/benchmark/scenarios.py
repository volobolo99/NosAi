from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from app.world_model.state import WorldState, EntityState
from app.world_model.actions import WorldAction

@dataclass(frozen=True)
class ScenarioSpec:
    name: str
    target_hp: float
    player_hp: float = 100.0
    attack5_risk: float = 0.01
    attack10_risk: float = 0.08
    attack5_self_damage: float = 0.0
    attack10_self_damage: float = 0.0
    terminal_bonus: float = 10.0
    step_cost: float = 0.0
    risk_cost: float = 0.0
    ood: float = 0.0
    shift: float = 0.0

class ScenarioEnv:
    def __init__(self, spec: ScenarioSpec):
        self.spec = spec

    def reset(self) -> WorldState:
        return WorldState(
            tick=0,
            character={"hp": self.spec.player_hp, "mp": 50.0},
            entities={"mob:1": EntityState("mob:1", "mob", {"hp": self.spec.target_hp})},
            map_id=self.spec.name,
            flags={"ood": self.spec.ood, "shift": self.spec.shift},
        )

    def actions(self, state: WorldState) -> list[WorldAction]:
        target = state.entities.get("mob:1")
        hp = float(target.attributes.get("hp", 0.0)) if target else 0.0
        if hp <= 0:
            return []
        return [
            WorldAction("attack5", "ATTACK", {"target_id": "mob:1", "damage": 5.0, "risk": self.spec.attack5_risk, "self_damage": self.spec.attack5_self_damage}),
            WorldAction("attack10", "ATTACK", {"target_id": "mob:1", "damage": 10.0, "risk": self.spec.attack10_risk, "self_damage": self.spec.attack10_self_damage}),
        ]

    def step(self, state: WorldState, action: WorldAction):
        next_state = state.copy()
        next_state.tick += 1
        target = next_state.entities.get("mob:1")
        if target is None:
            return next_state, -1.0, True, {"risk": 0.0, "terminal": False}
        damage = float(action.parameters.get("damage", 0.0))
        risk = float(action.parameters.get("risk", 0.0))
        self_damage = float(action.parameters.get("self_damage", 0.0))
        target = EntityState(target.entity_id, target.entity_type, dict(target.attributes))
        hp = max(0.0, float(target.attributes.get("hp", 0.0)) - damage)
        target.attributes["hp"] = hp
        next_state.entities[target.entity_id] = target
        character = dict(next_state.character)
        character["hp"] = max(0.0, float(character.get("hp", self.spec.player_hp)) - self_damage)
        next_state.character = character
        done = hp <= 0.0 or character["hp"] <= 0.0
        reward = 1.0 - self.spec.step_cost - self.spec.risk_cost * risk
        if hp <= 0.0:
            reward += self.spec.terminal_bonus
        if character["hp"] <= 0.0:
            reward -= 10.0
        return next_state, reward, done, {"risk": risk, "terminal": hp <= 0.0, "player_dead": character["hp"] <= 0.0}


def default_scenarios() -> tuple[ScenarioSpec, ...]:
    return (
        ScenarioSpec("easy", target_hp=20.0),
        ScenarioSpec("long_horizon", target_hp=50.0, step_cost=0.05),
        ScenarioSpec("risky_burst", target_hp=40.0, attack10_risk=0.35, risk_cost=2.0),
        ScenarioSpec("fragile", target_hp=40.0, player_hp=15.0, attack10_risk=0.25, attack10_self_damage=8.0, attack5_self_damage=3.0, risk_cost=1.5),
        ScenarioSpec("shifted", target_hp=35.0, attack10_risk=0.18, shift=0.8),
        ScenarioSpec("ood", target_hp=45.0, attack10_risk=0.22, ood=1.0, shift=0.9),
    )
