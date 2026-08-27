"""Observation-only runtime boundary for G3.5.

This module records runtime observations without issuing commands or performing
process/input/network automation. It is intentionally provider-neutral.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Mapping


@dataclass(frozen=True)
class Observation:
    kind: str
    payload: tuple[tuple[str, str], ...] = ()
    timestamp: float = field(default_factory=time)


class ObservationBuffer:
    def __init__(self, max_items: int = 256) -> None:
        if max_items < 1:
            raise ValueError("max_items must be positive")
        self._max_items = max_items
        self._items: list[Observation] = []

    def record(self, kind: str, payload: Mapping[str, str] | None = None) -> Observation:
        if not kind or not kind.strip():
            raise ValueError("kind must be non-empty")
        observation = Observation(kind.strip(), tuple(sorted((payload or {}).items())))
        self._items.append(observation)
        del self._items[:-self._max_items]
        return observation

    def snapshot(self) -> tuple[Observation, ...]:
        return tuple(self._items)


class KillSwitch:
    """Explicit runtime safety latch; starts engaged."""

    def __init__(self) -> None:
        self._engaged = True

    @property
    def engaged(self) -> bool:
        return self._engaged

    def engage(self) -> None:
        self._engaged = True

    def release(self) -> None:
        # G3.5 observation-only mode never releases the switch.
        self._engaged = True

    def allows_execution(self) -> bool:
        return False
