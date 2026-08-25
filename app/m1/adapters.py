"""Adapters connecting the M1 learning foundation to the v4.8 domain model.

The adapters keep M1 independent from WorldState/WorldAction while allowing the
existing sandbox and learning loop to emit normalized M1 transitions.
"""
from dataclasses import dataclass
from typing import Any

from app.world_model.state import WorldState
from app.world_model.actions import WorldAction
from app.world_model.simple_nostale_sandbox import SimpleNosTaleSandbox
from .core.types import State, Action, Prediction, Transition


def encode_world_state(state: WorldState) -> tuple[float, ...]:
    """Create a deterministic numeric summary suitable for M1/OOD/latent models."""
    hp = float(state.character.get("hp", 0))
    mp = float(state.character.get("mp", 0))
    inventory_total = float(sum(state.inventory.values()))
    entity_count = float(len(state.entities))
    entity_hp = float(sum(float(e.attributes.get("hp", 0)) for e in state.entities.values()))
    return (float(state.tick), hp, mp, inventory_total, entity_count, entity_hp)


def to_m1_state(state: WorldState, scenario_id: str = "sandbox") -> State:
    return State(
        features=encode_world_state(state),
        timestamp=state.tick,
        scenario_id=scenario_id,
        metadata={"world_state": state, "ood": float(state.flags.get("ood", 0.0)), "shift": float(state.flags.get("shift", 0.0))},
    )


def to_m1_action(action: WorldAction) -> Action:
    return Action(id=action.action_id, parameters={"kind": action.kind, **action.parameters})


def to_world_action(action: Action) -> WorldAction:
    params = dict(action.parameters)
    kind = params.pop("kind", action.id)
    return WorldAction(action_id=action.id, kind=kind, parameters=params)


class SandboxWorldModel:
    """M1 WorldModel backend backed by the existing deterministic sandbox."""
    def __init__(self, reward_fn=None):
        self.sandbox = SimpleNosTaleSandbox()
        self.reward_fn = reward_fn or self._default_reward

    @staticmethod
    def _default_reward(events):
        reward = 0.0
        if "DAMAGE" in events: reward += 1.0
        if "TARGET_DEFEATED" in events: reward += 10.0
        if "ITEM_USED" in events: reward -= 0.5
        if "MOVED" in events: reward -= 0.1
        return reward

    def predict(self, state: State, action: Action) -> Prediction:
        world_state = state.metadata.get("world_state")
        if not isinstance(world_state, WorldState):
            raise TypeError("SandboxWorldModel requires State.metadata['world_state']")
        next_world, events = self.sandbox.apply(world_state, to_world_action(action))
        next_state = to_m1_state(next_world, state.scenario_id)
        reward = float(self.reward_fn(events))
        target = next_world.entities.get("mob:1")
        done = bool(target and target.attributes.get("hp", 100) <= 0)
        return Prediction(next_state, reward, 1.0 if done else 0.0, reward)

    def rollout(self, state, actions):
        out = []
        current = state
        for action in actions:
            p = self.predict(current, action)
            out.append(p)
            current = p.next_state
        return out

    def uncertainty(self, state, action):
        from .core.types import Uncertainty
        return Uncertainty(epistemic=0.0, aleatoric=0.0, confidence=1.0)
