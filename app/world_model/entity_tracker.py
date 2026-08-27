"""Stable temporal tracking for observation-only entities."""
from __future__ import annotations

from dataclasses import dataclass
from math import hypot

from .state import EntityState, WorldState


@dataclass(frozen=True)
class TrackingConfig:
    max_distance: float = 80.0
    max_missed_ticks: int = 3


class EntityTracker:
    """Associate detections with stable IDs and retain short occlusions."""

    def __init__(self, config: TrackingConfig | None = None) -> None:
        self.config = config or TrackingConfig()
        if self.config.max_distance <= 0 or self.config.max_missed_ticks < 0:
            raise ValueError("invalid tracking configuration")
        self._next_id = 1
        self._missed: dict[str, int] = {}

    def track(self, previous: WorldState | None, detections: list[EntityState]) -> list[EntityState]:
        previous_entities = {} if previous is None else self.active_previous(previous)
        candidates = list(previous_entities.values())
        result: list[EntityState] = []
        matched: set[str] = set()

        for detection in detections:
            best = min(
                (candidate for candidate in candidates if candidate.entity_id not in matched and candidate.entity_type == detection.entity_type),
                key=lambda candidate: self._distance(candidate, detection),
                default=None,
            )
            if best is not None and self._distance(best, detection) <= self.config.max_distance:
                entity_id = best.entity_id
                matched.add(entity_id)
            else:
                entity_id = self._new_id(detection.entity_type)
            self._missed[entity_id] = 0
            result.append(EntityState(entity_id, detection.entity_type, dict(detection.attributes), detection.confidence, detection.source, detection.last_seen_tick))

        for entity_id, entity in previous_entities.items():
            if entity_id not in matched and entity_id not in {e.entity_id for e in result}:
                missed = self._missed.get(entity_id, 0) + 1
                self._missed[entity_id] = missed
                if missed <= self.config.max_missed_ticks:
                    result.append(EntityState(entity.entity_id, entity.entity_type, dict(entity.attributes), max(0.0, entity.confidence * 0.95), "tracking_prediction", entity.last_seen_tick))
        return result

    def active_previous(self, previous: WorldState | None) -> dict[str, EntityState]:
        if previous is None:
            return {}
        return {entity_id: entity for entity_id, entity in previous.entities.items() if self._missed.get(entity_id, 0) <= self.config.max_missed_ticks}

    def _new_id(self, entity_type: str) -> str:
        entity_id = f"{entity_type}:{self._next_id}"
        self._next_id += 1
        return entity_id

    @staticmethod
    def _distance(a: EntityState, b: EntityState) -> float:
        ax, ay = a.attributes.get("x"), a.attributes.get("y")
        bx, by = b.attributes.get("x"), b.attributes.get("y")
        if None in (ax, ay, bx, by):
            return float("inf")
        return hypot(float(ax) - float(bx), float(ay) - float(by))
