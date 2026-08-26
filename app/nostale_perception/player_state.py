"""Conservative player-state projection from validated semantic observations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .network_decoder import DecodedObservation


@dataclass
class PlayerState:
    entity_id: int | None = None
    x: float | None = None
    y: float | None = None
    hp: int | None = None
    hp_max: int | None = None
    mp: int | None = None
    mp_max: int | None = None
    condition: str | None = None
    confidence: float = 0.0
    revision: int = 0

    def apply(self, observation: DecodedObservation) -> bool:
        payload: Mapping[str, object] = observation.payload
        if observation.kind == "player_info":
            entity_id = payload.get("entity_id")
            if not isinstance(entity_id, int):
                return False
            self.entity_id = entity_id
            for name in ("hp", "hp_max", "mp", "mp_max"):
                value = payload.get(name)
                if value is not None and not isinstance(value, int):
                    return False
                setattr(self, name, value)
        elif observation.kind == "player_condition":
            condition = payload.get("condition")
            if not isinstance(condition, str):
                return False
            self.condition = condition
        else:
            return False
        self.confidence = max(self.confidence, observation.confidence)
        self.revision += 1
        return True
