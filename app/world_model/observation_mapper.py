"""Convert observation-only perception output into the canonical WorldState."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.client.multi_entity import MultiEntityObservation

from .state import EntityState, WorldState


class ObservationMapper:
    """Fuse observation-only perception output into a WorldState snapshot.

    The mapper never performs client I/O. It only translates detections into
    structured state and preserves confidence/source metadata for Brain and
    Memory consumers.
    """

    def update(
        self,
        previous: WorldState | None,
        observation: MultiEntityObservation,
        *,
        map_id: str | None = None,
        tick: int | None = None,
    ) -> WorldState:
        state = (previous or WorldState()).copy()
        next_tick = state.tick + 1 if tick is None else tick
        if next_tick < state.tick:
            raise ValueError("observation tick cannot move backwards")
        state.tick = next_tick
        state.revision += 1
        state.observed_at = datetime.now(timezone.utc).isoformat()
        state.source = "visual_perception"
        if map_id is not None:
            state.map_id = map_id

        for detection in observation.all_entities:
            entity_id = self._entity_id(detection)
            state.entities[entity_id] = EntityState(
                entity_id=entity_id,
                entity_type=detection.kind,
                attributes={
                    "x": detection.x,
                    "y": detection.y,
                    "width": detection.width,
                    "height": detection.height,
                },
                confidence=detection.confidence,
                source=detection.source,
                last_seen_tick=state.tick,
            )

        if observation.player:
            player = max(observation.player, key=lambda d: d.confidence)
            state.character.update(
                {
                    "screen_x": player.x,
                    "screen_y": player.y,
                    "vision_confidence": player.confidence,
                }
            )
        return state

    @staticmethod
    def _entity_id(detection: Any) -> str:
        return f"vision:{detection.kind}:{detection.x}:{detection.y}:{detection.width}:{detection.height}"
