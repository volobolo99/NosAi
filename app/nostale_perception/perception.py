"""Provider-neutral, read-only perception pipeline for NosTale."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Callable, Mapping, Protocol

from app.zmsia.core.contracts import Observation

from .gamestate import GameState, GameStateBuilder, PlayerState, WorldEntity


@dataclass(frozen=True)
class Frame:
    """Immutable frame metadata plus optional pixel payload supplied by a source."""

    frame_id: str
    timestamp_ms: int
    width: int
    height: int
    pixels: bytes | None = None
    source: str = "unknown"

    @property
    def sha256(self) -> str | None:
        return sha256(self.pixels).hexdigest() if self.pixels is not None else None


class FrameSource(Protocol):
    """Read-only frame acquisition boundary."""

    def capture(self) -> Frame:
        ...


@dataclass(frozen=True)
class PerceptionResult:
    observation: Observation
    game_state: GameState


class ObservationPipeline:
    """Convert one captured frame and structured detectors into a GameState.

    Detectors are pure/injected functions. No OCR, model, memory access or input
    transport is hard-coded here; this keeps replay deterministic and permits
    local CV/ML providers to be added later without changing the ZMSIA boundary.
    """

    def __init__(
        self,
        source: FrameSource,
        *,
        player_detector: Callable[[Frame], Mapping[str, Any]] | None = None,
        entity_detector: Callable[[Frame], list[Mapping[str, Any]]] | None = None,
        map_detector: Callable[[Frame], str | None] | None = None,
        ui_detector: Callable[[Frame], Mapping[str, Any]] | None = None,
    ) -> None:
        self._source = source
        self._player_detector = player_detector or (lambda _frame: {})
        self._entity_detector = entity_detector or (lambda _frame: [])
        self._map_detector = map_detector or (lambda _frame: None)
        self._ui_detector = ui_detector or (lambda _frame: {})

    def observe(self, *, client_pid: int | None = None, window_rect: dict[str, int] | None = None) -> PerceptionResult:
        frame = self._source.capture()
        if frame.width <= 0 or frame.height <= 0:
            raise ValueError("captured frame dimensions must be positive")

        observation = Observation(
            observation_id=frame.frame_id,
            timestamp_ms=frame.timestamp_ms,
            source=frame.source,
            data={
                "frame_sha256": frame.sha256,
                "width": frame.width,
                "height": frame.height,
            },
            confidence=1.0,
        )

        player_data = dict(self._player_detector(frame))
        player = PlayerState(
            hp=player_data.get("hp"), hp_max=player_data.get("hp_max"),
            mp=player_data.get("mp"), mp_max=player_data.get("mp_max"),
            x=player_data.get("x"), y=player_data.get("y"),
            level=player_data.get("level"), name=player_data.get("name"),
            target_id=player_data.get("target_id"),
            confidence=float(player_data.get("confidence", 0.0)),
        )

        entities = tuple(
            WorldEntity(
                entity_id=str(item["entity_id"]),
                entity_type=str(item["entity_type"]),
                x=item.get("x"), y=item.get("y"),
                hp=item.get("hp"), hp_max=item.get("hp_max"),
                name=item.get("name"), hostile=item.get("hostile"),
                visible=bool(item.get("visible", True)),
                confidence=float(item.get("confidence", 0.0)),
            )
            for item in self._entity_detector(frame)
        )

        confidence_values = [player.confidence, *(item.confidence for item in entities)]
        confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0.0
        builder = (
            GameStateBuilder(state_id=f"state:{frame.frame_id}", timestamp_ms=frame.timestamp_ms)
            .client(pid=client_pid, window_rect=window_rect or {})
            .map(self._map_detector(frame))
            .player(player)
            .entities(entities)
            .ui(dict(self._ui_detector(frame)))
            .source(frame.frame_id)
            .quality(stale=False, confidence=confidence)
        )
        return PerceptionResult(observation=observation, game_state=builder.build())
