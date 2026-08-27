"""Pure, deterministic state-transition model used by simulation and replay."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from .actions import WorldAction
from .state import EntityState, WorldState


class WorldModel:
    """Apply explicit, data-only transitions without touching the live client.

    Unknown action kinds fail closed. This keeps simulation/replay deterministic
    and prevents the world model from becoming an implicit game-control layer.
    """

    SUPPORTED_ACTIONS = frozenset(
        {
            "advance_tick",
            "set_flag",
            "set_character",
            "set_inventory",
            "upsert_entity",
            "remove_entity",
            "set_map",
        }
    )

    def apply(self, state: WorldState, action: WorldAction, rng: Any = None) -> WorldState:
        if action.kind not in self.SUPPORTED_ACTIONS:
            raise ValueError(f"unsupported world action: {action.kind}")
        next_state = state.copy().touch(source="simulation")
        p = deepcopy(action.parameters)

        if action.kind == "advance_tick":
            next_state.tick = max(next_state.tick, int(p.get("tick", next_state.tick)))
        elif action.kind == "set_flag":
            key = str(p["key"])
            next_state.flags[key] = p.get("value")
        elif action.kind == "set_character":
            key = str(p["key"])
            next_state.character[key] = p.get("value")
        elif action.kind == "set_inventory":
            key = str(p["item_id"])
            quantity = int(p["quantity"])
            if quantity < 0:
                raise ValueError("inventory quantity cannot be negative")
            next_state.inventory[key] = quantity
        elif action.kind == "upsert_entity":
            entity = p["entity"]
            entity_id = str(entity["entity_id"])
            next_state.entities[entity_id] = EntityState(**entity)
        elif action.kind == "remove_entity":
            next_state.entities.pop(str(p["entity_id"]), None)
        elif action.kind == "set_map":
            next_state.map_id = None if p.get("map_id") is None else str(p["map_id"])

        return next_state

    def observe(self, state: WorldState) -> WorldState:
        """Return an isolated snapshot; never expose internal mutable state."""
        return state.copy()
