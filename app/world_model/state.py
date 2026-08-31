"""Canonical, serializable world-state contracts for NosAi.

The state is observation/simulation friendly: every mutable collection is
owned by the state instance, confidence/provenance are explicit, and copies
are deep enough to prevent nested aliasing during replay or planning.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class EntityState:
    entity_id: str
    entity_type: str
    attributes: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    source: str = "runtime"
    last_seen_tick: int = 0

    def __post_init__(self) -> None:
        self.confidence = min(1.0, max(0.0, float(self.confidence)))


@dataclass
class WorldState:
    tick: int = 0
    character: dict[str, Any] = field(default_factory=dict)
    entities: dict[str, EntityState] = field(default_factory=dict)
    map_id: str | None = None
    inventory: dict[str, int] = field(default_factory=dict)
    quests: dict[str, str] = field(default_factory=dict)
    flags: dict[str, Any] = field(default_factory=dict)
    observed_at: str | None = None
    revision: int = 0
    source: str = "runtime"

    def __post_init__(self) -> None:
        if self.tick < 0 or self.revision < 0:
            raise ValueError("tick and revision must be non-negative")
        if self.observed_at is None:
            self.observed_at = datetime.now(timezone.utc).isoformat()

    def copy(self) -> "WorldState":
        """Return an isolated state suitable for planning/replay."""
        return deepcopy(self)

    def touch(self, *, tick: int | None = None, source: str | None = None) -> "WorldState":
        """Advance the state revision without mutating the original."""
        next_state = self.copy()
        if tick is not None:
            if tick < next_state.tick:
                raise ValueError("tick cannot move backwards")
            next_state.tick = tick
        else:
            next_state.tick += 1
        next_state.revision += 1
        next_state.observed_at = datetime.now(timezone.utc).isoformat()
        if source is not None:
            next_state.source = source
        return next_state

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "WorldState":
        entities = {
            str(entity_id): EntityState(**entity)
            for entity_id, entity in payload.get("entities", {}).items()
        }
        data = dict(payload)
        data["entities"] = entities
        return cls(**data)
