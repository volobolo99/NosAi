"""Canonical player projection used by the NosTale GameState."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .network_decoder import DecodedObservation


@dataclass
class PlayerState:
    entity_id: int | None = None
    hp: float | None = None
    hp_max: float | None = None
    mp: float | None = None
    mp_max: float | None = None

    def apply(self, observation: DecodedObservation) -> bool:
        payload: dict[str, Any] = dict(observation.payload)
        changed = False
        for field_name in ("entity_id", "hp", "hp_max", "mp", "mp_max"):
            if field_name not in payload:
                continue
            value = payload[field_name]
            if field_name == "entity_id":
                value = int(value)
            else:
                value = float(value)
            if getattr(self, field_name) != value:
                setattr(self, field_name, value)
                changed = True
        return changed
