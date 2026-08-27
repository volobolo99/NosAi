"""Stable temporal tracking for observation-only entities."""
from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from typing import Any

from .state import EntityState, WorldState


@dataclass(frozen=True)
class TrackingConfig:
    max_distance: float = 80.0
    max_missed_ticks: int = 3


class EntityTracker:
    """Associate detections with stable IDs across consecutive observations."""

    def __init__(self, config: TrackingConfig | None = None) -> None:
        self.config = config or TrackingConfig()
        self._next_id = 1
        self._missed: dict[str, int] = {}

    def track(self, previous: WorldState | None, detections: list[EntityState]) -> list[EntityState]:
        previous_entities = {} if previous is None else previous.entities
        candidates = list(previous_entities.values())
        result: list[EntityState] = []
        matched: set[str] = set()

        for detection in detections:
            best: EntityState | None = None
            best_distance = float("inf")
            for candidate in candidates:
                if candidate.entity_id in matched or candidate.entity_type != detection.entity_type:
                    continue
                distance = self._distance(candidate, detection)
                if distance <= self.config.max_distance and distance < best_distance:
                    best, best_distance = candidate, distance
            entity_id = best.entity_id if best else self._new_id(detection.entity_type)
            if best:
                matched.add(best.entity_id)
            self._missed[entity_id] = 0
            result.append(
                EntityState(
                    entity_id=entity_id,
                    entity_type=detection.entity_type,
                    attributes=dict(detection.attributes),
                    confidence=detection.confidence,
                    source=detection.source,
                    last_seen_tick=detection.last_seen_tick,
                )
            )

        for entity_id in previous_entities:
            if entity_id not in matched and entity_id not in {e.entity_id for e in result}:
                self._missed[entity_id] = self._missed.get(entity_id, 0) + 1

        return result

    def active_previous(self, previous: WorldState | None) -> dict[str, EntityState]:
        if previous is None:
            return {}
        return {
            entity_id: entity
            for entity_id, entity in previous.entities.items()
            if self._missed.get(entity_id, 0) <= self.config.max_missed_ticks
        }

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
