"""Observation-only minimap navigation and path planning.

This module converts minimap observations into a conservative grid and computes
candidate paths with A*. It never sends input or moves the NosTale client.
"""
from __future__ import annotations

from dataclasses import dataclass
import heapq
from math import hypot
from typing import Iterable

from .multi_entity import Detection, MinimapObservation


@dataclass(frozen=True)
class GridPoint:
    x: int
    y: int


@dataclass(frozen=True)
class PathPlan:
    points: tuple[GridPoint, ...]
    distance: float
    confidence: float
    source: str = "minimap_astar"
    observation_only: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "points": [{"x": p.x, "y": p.y} for p in self.points],
            "distance": round(self.distance, 3),
            "confidence": round(self.confidence, 4),
            "source": self.source,
            "observation_only": self.observation_only,
        }


def _neighbors(p: GridPoint) -> Iterable[GridPoint]:
    yield GridPoint(p.x + 1, p.y)
    yield GridPoint(p.x - 1, p.y)
    yield GridPoint(p.x, p.y + 1)
    yield GridPoint(p.x, p.y - 1)


def astar(
    start: GridPoint,
    goal: GridPoint,
    blocked: set[GridPoint],
    width: int,
    height: int,
) -> PathPlan | None:
    if not (0 <= start.x < width and 0 <= start.y < height):
        return None
    if not (0 <= goal.x < width and 0 <= goal.y < height):
        return None
    if start in blocked or goal in blocked:
        return None

    queue: list[tuple[float, int, GridPoint]] = []
    sequence = 0
    heapq.heappush(queue, (0.0, sequence, start))
    came_from: dict[GridPoint, GridPoint] = {}
    cost = {start: 0.0}

    while queue:
        _, _, current = heapq.heappop(queue)
        if current == goal:
            points = [current]
            while current in came_from:
                current = came_from[current]
                points.append(current)
            points.reverse()
            distance = max(0, len(points) - 1)
            return PathPlan(tuple(points), float(distance), 1.0)

        for nxt in _neighbors(current):
            if not (0 <= nxt.x < width and 0 <= nxt.y < height):
                continue
            if nxt in blocked:
                continue
            new_cost = cost[current] + 1.0
            if new_cost >= cost.get(nxt, float("inf")):
                continue
            cost[nxt] = new_cost
            came_from[nxt] = current
            sequence += 1
            priority = new_cost + hypot(goal.x - nxt.x, goal.y - nxt.y)
            heapq.heappush(queue, (priority, sequence, nxt))
    return None


class MinimapPathPlanner:
    """Build candidate paths from explicit minimap coordinates only."""

    def __init__(self, grid_width: int = 64, grid_height: int = 64) -> None:
        self.grid_width = grid_width
        self.grid_height = grid_height

    @staticmethod
    def _center(detection: Detection) -> tuple[float, float]:
        return detection.x + detection.width / 2, detection.y + detection.height / 2

    def plan(
        self,
        minimap: MinimapObservation,
        start: GridPoint,
        goal: GridPoint,
        blocked: set[GridPoint] | None = None,
    ) -> PathPlan | None:
        del minimap
        return astar(
            start,
            goal,
            blocked or set(),
            self.grid_width,
            self.grid_height,
        )

    def nearest_entity(
        self, minimap: MinimapObservation, x: float, y: float, kind: str
    ) -> Detection | None:
        candidates = [d for d in minimap.detections if d.kind == kind]
        if not candidates:
            return None
        return min(candidates, key=lambda d: hypot(self._center(d)[0] - x, self._center(d)[1] - y))
