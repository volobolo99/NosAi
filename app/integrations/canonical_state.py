"""Canonical, provider-neutral state used by perception and decision layers."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class EntityState:
    entity_id: str
    kind: str
    x: float | None = None
    y: float | None = None
    hp: int | None = None
    mp: int | None = None
    name: str | None = None
    target_id: str | None = None
    source: str = "unknown"


@dataclass(frozen=True)
class PlayerState:
    entity_id: str | None = None
    x: float | None = None
    y: float | None = None
    hp: int | None = None
    max_hp: int | None = None
    mp: int | None = None
    max_mp: int | None = None
    direction: int | None = None
    target_id: str | None = None


@dataclass(frozen=True)
class CanonicalGameState:
    timestamp_ms: int
    client_pid: int | None
    map_id: str | None
    player: PlayerState
    entities: tuple[EntityState, ...] = field(default_factory=tuple)
    packets_observed: int = 0
    frame_sha256: str | None = None
    sources: tuple[str, ...] = field(default_factory=tuple)
    quality: float = 0.0
    sequence: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def empty(cls, timestamp_ms: int, client_pid: int | None = None) -> "CanonicalGameState":
        return cls(timestamp_ms=timestamp_ms, client_pid=client_pid, map_id=None, player=PlayerState())
