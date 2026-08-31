"""Apply conservative normalized observations to the canonical world model."""
from __future__ import annotations

from typing import Any, Mapping

from .world_state import WorldState


def apply_observation(world: WorldState, observation: Mapping[str, Any], sequence: int | None = None) -> str:
    """Apply only explicit entity observations/removals.

    Expected normalized shape: ``{"event": "in"|"mv"|"out", "entity_id": ..., "fields": {...}}``.
    Unknown events are ignored rather than guessed.
    """
    event = observation.get("event")
    entity_id = observation.get("entity_id")
    if event == "out":
        if entity_id is not None:
            world.remove_entity(entity_id, sequence)
        return "removed"
    if event in {"in", "mv"} and entity_id is not None:
        fields = observation.get("fields", {})
        if not isinstance(fields, Mapping):
            raise ValueError("observation fields must be a mapping")
        world.observe_entity(entity_id, fields, sequence)
        return "updated"
    return "ignored"
