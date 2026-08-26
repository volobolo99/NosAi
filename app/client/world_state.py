"""Normalized, observation-only world state for the NosTale runtime."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .nostale_windows import ClientState
from .windows_hud import HudObservation


@dataclass(frozen=True)
class VisualWorldState:
    client: dict[str, Any]
    hud: HudObservation | None
    entities: tuple[dict[str, Any], ...] = ()
    source: str = "windows_visual_perception"
    observation_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "client": self.client,
            "hud": None if self.hud is None else {
                "text": self.hud.text,
                "hp": self.hud.hp,
                "mp": self.hud.mp,
                "level": self.hud.level,
                "source": self.hud.source,
                "observation_only": self.hud.observation_only,
            },
            "entities": list(self.entities),
            "source": self.source,
            "observation_only": self.observation_only,
        }


def from_client_state(state: ClientState, hud: HudObservation | None = None) -> VisualWorldState:
    return VisualWorldState(client=dict(state.payload), hud=hud)
