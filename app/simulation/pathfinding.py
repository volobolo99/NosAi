"""HPA*-compatible planning primitives with a dynamic hazard costmap.

The current implementation uses weighted A* on a grid. The public seam is
small enough to replace the local search with hierarchical cluster search
without changing callers once map sizes justify it.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass


@dataclass(frozen=True)
class HazardCell:
    aoe: float = 0.0
    aggro_overlap: float = 0.0
    los_block: float = 0.0

    def cost(self, w1: float = 5.0, w2: float = 3.0, w3: float = 2.0) -> float:
        return w1 * max(0.0, self.aoe) + w2 * max(0.0, self.aggro_overlap) + w3 * max(0.0, self.los_block)


class GridMap:
    def __init__(self, width: int, height: int) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("grid dimensions must be positive")
        self.width, self.height = width, height
        self.blocked: set[tuple[int, int]] = set()
        self.hazards: dict[tuple[int, int], HazardCell] = {}

    def set_blocked(self, x: int, y: int, blocked: bool = True) -> None:
        self._check(x, y)
        if blocked:
            self.blocked.add((x, y))
        else:
            self.blocked.discard((x, y))

    def set_hazard(self, x: int, y: int, hazard: HazardCell) -> None:
        self._check(x, y)
        self.hazards[(x, y)] = hazard

    def _check(self, x: int, y: int) -> None:
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError("cell outside grid")


class PathPlanner:
    def __init__(self, grid: GridMap, base_cost: float = 1.0) -> None:
        if base_cost <= 0:
            raise ValueError("base_cost must be positive")
        self.grid = grid
        self.base_cost = base_cost

    def plan(self, start: tuple[int, int], goal: tuple[int, int]) -> list[tuple[int, int]]:
        if start in self.grid.blocked or goal in self.grid.blocked:
            return []
        frontier: list[tuple[float, int, tuple[int, int]]] = [(0.0, 0, start)]
        came_from: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
        cost_so_far = {start: 0.0}
        counter = 0
        while frontier:
            _, _, current = heapq.heappop(frontier)
            if current == goal:
                return self._reconstruct(came_from, goal)
            for nxt in self._neighbors(current):
                step = self.base_cost + self.grid.hazards.get(nxt, HazardCell()).cost()
                new_cost = cost_so_far[current] + step
                if new_cost < cost_so_far.get(nxt, float("inf")):
                    cost_so_far[nxt] = new_cost
                    counter += 1
                    priority = new_cost + self._heuristic(nxt, goal)
                    heapq.heappush(frontier, (priority, counter, nxt))
                    came_from[nxt] = current
        return []

    def _neighbors(self, cell: tuple[int, int]):
        x, y = cell
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid.width and 0 <= ny < self.grid.height and (nx, ny) not in self.grid.blocked:
                yield nx, ny

    @staticmethod
    def _heuristic(a: tuple[int, int], b: tuple[int, int]) -> float:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @staticmethod
    def _reconstruct(came_from, goal):
        path = []
        current = goal
        while current is not None:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path
