"""Unified deterministic GameState projection for NosAi perception."""
from __future__ import annotations

from dataclasses import dataclass

from .network_decoder import DecodedObservation
from .player_state import PlayerState
from .world_model import WorldModel


@dataclass
class GameState:
    player: PlayerState
    world: WorldModel
    revision: int = 0

    @classmethod
    def empty(cls) -> "GameState":
        return cls(player=PlayerState(), world=WorldModel())

    def apply(self, observation: DecodedObservation) -> bool:
        applied = self.player.apply(observation) if observation.kind in {"player_info", "player_condition"} else self.world.apply(observation)
        if applied:
            self.revision += 1
        return applied
