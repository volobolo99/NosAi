"""Normalized, observation-only world state for the NosTale runtime."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .nostale_windows import ClientState
from .windows_hud import HudObservation
from .multi_entity import MultiEntityObservation


@dataclass(frozen=True)
class VisualWorldState:
    client: dict[str, Any]
    hud: HudObservation | None
    entities: tuple[dict[str, Any], ...] = ()
    perception: dict[str, Any] | None = None
    navigation: dict[str, Any] | None = None
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
            "perception": self.perception,
            "navigation": self.navigation,
            "source": self.source,
            "observation_only": self.observation_only,
        }


def from_client_state(
    state: ClientState,
    hud: HudObservation | None = None,
    perception: MultiEntityObservation | None = None,
    navigation: dict[str, Any] | None = None,
) -> VisualWorldState:
    entities: tuple[dict[str, Any], ...] = ()
    perception_dict = None
    if perception is not None:
        perception_dict = perception.to_dict()
        entities = tuple(
            item
            for kind in ("player", "npc", "mob")
            for item in perception_dict[kind]
        )
    return VisualWorldState(
        client=dict(state.payload),
        hud=hud,
        entities=entities,
        perception=perception_dict,
        navigation=navigation,
    )
