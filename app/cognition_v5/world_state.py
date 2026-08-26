"""Versioned, immutable world-state projection for the v5 cognitive loop."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from time import monotonic
from typing import Mapping


@dataclass(frozen=True, slots=True)
class WorldState:
    """Normalized state consumed by cognition; adapters never mutate it directly."""

    version: int = 1
    timestamp: float = field(default_factory=monotonic)
    values: Mapping[str, object] = field(default_factory=dict)

    def evolve(self, **updates: object) -> "WorldState":
        merged = dict(self.values)
        merged.update(updates)
        return replace(self, version=self.version + 1, timestamp=monotonic(), values=merged)

    def get(self, key: str, default: object = None) -> object:
        return self.values.get(key, default)
