"""Canonical, serializable GameState contracts for NosTale perception."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from math import isfinite
from typing import Any


def _confidence(value: float) -> float:
    if not isfinite(value):
        raise ValueError("confidence must be finite")
    return max(0.0, min(1.0, value))


@dataclass(frozen=True)
class PlayerState:
    """Observed player state; unknown values remain None instead of guesses."""

    hp: int | None = None
    hp_max: int | None = None
    mp: int | None = None
    mp_max: int | None = None
    x: float | None = None
    y: float | None = None
    level: int | None = None
    name: str | None = None
    target_id: str | None = None
    confidence: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "confidence", _confidence(self.confidence))


@dataclass(frozen=True)
class WorldEntity:
    """Observed world entity with explicit type and uncertainty."""

    entity_id: str
    entity_type: str
    x: float | None = None
    y: float | None = None
    hp: int | None = None
    hp_max: int | None = None
    name: str | None = None
    hostile: bool | None = None
    visible: bool = True
    confidence: float = 0.0

    def __post_init__(self) -> None:
        if not self.entity_id:
            raise ValueError("entity_id is required")
        if not self.entity_type:
            raise ValueError("entity_type is required")
        object.__setattr__(self, "confidence", _confidence(self.confidence))


@dataclass(frozen=True)
class GameState:
    """Canonical read-only world snapshot consumed by ZMSIA."""

    schema_version: int
    state_id: str
    timestamp_ms: int
    client_pid: int | None
    window_rect: dict[str, int]
    map_name: str | None
    player: PlayerState
    entities: tuple[WorldEntity, ...] = ()
    ui: dict[str, Any] = field(default_factory=dict)
    source_observation_ids: tuple[str, ...] = ()
    stale: bool = False
    overall_confidence: float = 0.0

    def __post_init__(self) -> None:
        if self.schema_version != 1:
            raise ValueError("unsupported GameState schema version")
        if self.timestamp_ms < 0:
            raise ValueError("timestamp_ms must be non-negative")
        object.__setattr__(self, "overall_confidence", _confidence(self.overall_confidence))

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation for telemetry/replay."""
        return asdict(self)


class GameStateBuilder:
    """Small deterministic builder used by perception providers and tests."""

    def __init__(self, *, state_id: str, timestamp_ms: int) -> None:
        self._state_id = state_id
        self._timestamp_ms = timestamp_ms
        self._client_pid: int | None = None
        self._window_rect: dict[str, int] = {}
        self._map_name: str | None = None
        self._player = PlayerState()
        self._entities: list[WorldEntity] = []
        self._ui: dict[str, Any] = {}
        self._source_ids: list[str] = []
        self._stale = False
        self._confidence = 0.0

    def client(self, *, pid: int | None, window_rect: dict[str, int]) -> "GameStateBuilder":
        self._client_pid = pid
        self._window_rect = dict(window_rect)
        return self

    def map(self, name: str | None) -> "GameStateBuilder":
        self._map_name = name
        return self

    def player(self, value: PlayerState) -> "GameStateBuilder":
        self._player = value
        return self

    def entities(self, values: list[WorldEntity] | tuple[WorldEntity, ...]) -> "GameStateBuilder":
        self._entities = list(values)
        return self

    def ui(self, value: dict[str, Any]) -> "GameStateBuilder":
        self._ui = dict(value)
        return self

    def source(self, *observation_ids: str) -> "GameStateBuilder":
        self._source_ids.extend(observation_ids)
        return self

    def quality(self, *, stale: bool, confidence: float) -> "GameStateBuilder":
        self._stale = stale
        self._confidence = confidence
        return self

    def build(self) -> GameState:
        return GameState(
            schema_version=1,
            state_id=self._state_id,
            timestamp_ms=self._timestamp_ms,
            client_pid=self._client_pid,
            window_rect=self._window_rect,
            map_name=self._map_name,
            player=self._player,
            entities=tuple(self._entities),
            ui=self._ui,
            source_observation_ids=tuple(dict.fromkeys(self._source_ids)),
            stale=self._stale,
            overall_confidence=self._confidence,
        )
