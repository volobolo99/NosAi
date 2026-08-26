"""Deterministic world-entity projection for NosTale observations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .network_decoder import DecodedObservation


@dataclass
class WorldEntity:
    entity_id: int
    x: float | None = None
    y: float | None = None


@dataclass
class WorldModel:
    entities: dict[int, WorldEntity] | None = None

    def __post_init__(self) -> None:
        if self.entities is None:
            self.entities = {}

    def apply(self, observation: DecodedObservation) -> bool:
        payload: dict[str, Any] = dict(observation.payload)
        if "entity_id" not in payload:
            return False
        entity_id = int(payload["entity_id"])
        entity = self.entities.get(entity_id)
        if entity is None:
            entity = WorldEntity(entity_id=entity_id)
            self.entities[entity_id] = entity
        changed = False
        for field_name in ("x", "y"):
            if field_name not in payload:
                continue
            value = float(payload[field_name])
            if getattr(entity, field_name) != value:
                setattr(entity, field_name, value)
                changed = True
        return changed
