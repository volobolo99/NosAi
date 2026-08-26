"""Deterministic world-model reducer for validated semantic observations."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .network_decoder import DecodedObservation


@dataclass
class EntityState:
    entity_id: int
    x: float | None = None
    y: float | None = None
    active: bool = True
    confidence: float = 0.0
    last_observation_id: str | None = None


@dataclass
class WorldModel:
    entities: dict[int, EntityState] = field(default_factory=dict)
    revision: int = 0

    def apply(self, observation: DecodedObservation) -> bool:
        payload: Mapping[str, object] = observation.payload
        entity_id = payload.get("entity_id")
        if not isinstance(entity_id, int):
            return False
        if observation.kind == "movement":
            x, y = payload.get("x"), payload.get("y")
            if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                return False
            entity = self.entities.setdefault(entity_id, EntityState(entity_id))
            entity.x, entity.y = float(x), float(y)
            entity.active = True
            entity.confidence = observation.confidence
            entity.last_observation_id = observation.source_observation_id
        elif observation.kind == "entity_remove_or_update":
            entity = self.entities.setdefault(entity_id, EntityState(entity_id))
            entity.active = False
            entity.confidence = observation.confidence
            entity.last_observation_id = observation.source_observation_id
        else:
            return False
        self.revision += 1
        return True
