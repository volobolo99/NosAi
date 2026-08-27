"""Convert observation-only perception output into canonical WorldState."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from app.client.multi_entity import MultiEntityObservation

from .entity_tracker import EntityTracker
from .hud_state import HudStateExtractor, HudValue
from .state import EntityState, WorldState


class ObservationMapper:
    """Fuse perception into WorldState while preserving confidence/provenance."""

    def __init__(self, tracker: EntityTracker | None = None, hud_extractor: HudStateExtractor | None = None) -> None:
        self.tracker = tracker or EntityTracker()
        self.hud_extractor = hud_extractor or HudStateExtractor()

    def update(self, previous: WorldState | None, observation: MultiEntityObservation, *, map_id: str | None = None, tick: int | None = None, hud: Mapping[str, HudValue] | None = None) -> WorldState:
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

        raw_entities = [
            EntityState(
                entity_id=self._entity_id(d),
                entity_type=d.kind,
                attributes={"x": d.x, "y": d.y, "width": d.width, "height": d.height},
                confidence=d.confidence,
                source=d.source,
                last_seen_tick=state.tick,
            )
            for d in observation.all_entities
        ]
        tracked = self.tracker.track(state, raw_entities)
        state.entities = {entity.entity_id: entity for entity in tracked}

        if observation.player:
            player = max(observation.player, key=lambda d: d.confidence)
            state.character.update({"screen_x": player.x, "screen_y": player.y, "vision_confidence": player.confidence})
        if hud:
            state.character.update(self.hud_extractor.extract(hud))
        return state

    @staticmethod
    def _entity_id(detection: Any) -> str:
        return f"vision:{detection.kind}:{detection.x}:{detection.y}:{detection.width}:{detection.height}"
