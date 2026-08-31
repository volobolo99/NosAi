"""In-memory world state updated only from normalized observations."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .entity_state import EntityState


@dataclass
class WorldState:
    entities: dict[int | str, EntityState] = field(default_factory=dict)
    sequence: int | None = None

    def observe_entity(self, entity_id: int | str, fields: Mapping[str, Any], sequence: int | None = None) -> EntityState:
        current = self.entities.get(entity_id, EntityState(entity_id=entity_id))
        updated = current.apply(fields, sequence)
        self.entities[entity_id] = updated
        if sequence is not None:
            self.sequence = sequence
        return updated

    def remove_entity(self, entity_id: int | str, sequence: int | None = None) -> bool:
        existed = entity_id in self.entities
        self.entities.pop(entity_id, None)
        if sequence is not None:
            self.sequence = sequence
        return existed
