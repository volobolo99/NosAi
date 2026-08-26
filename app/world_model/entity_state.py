"""Minimal canonical entity state used by the observation world model."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping


@dataclass(frozen=True)
class EntityState:
    entity_id: int | str
    x: int | float | None = None
    y: int | float | None = None
    direction: int | str | None = None
    hp_percent: int | float | None = None
    mp_percent: int | float | None = None
    name: str | None = None
    last_sequence: int | None = None

    def apply(self, fields: Mapping[str, Any], sequence: int | None = None) -> "EntityState":
        allowed = {"x", "y", "direction", "hp_percent", "mp_percent", "name"}
        updates = {key: fields[key] for key in allowed if key in fields}
        if sequence is not None:
            updates["last_sequence"] = sequence
        return replace(self, **updates)
