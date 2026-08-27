"""Observation-only runtime pipeline for the Block A perception boundary."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import uuid4

from app.client.multi_entity import MultiEntityObservation
from app.world_model import ObservationMapper, WorldState


@dataclass(frozen=True)
class ObservationEvent:
    correlation_id: str
    tick: int
    observed_at: str
    observation: dict[str, Any]
    world_state: dict[str, Any]
    observation_only: bool = True


class ObservationPipeline:
    """Fuse perception observations into WorldState and publish telemetry.

    This pipeline deliberately has no client-control dependency. A publisher
    may persist or stream events, but it cannot execute game actions through
    this interface.
    """

    def __init__(
        self,
        mapper: ObservationMapper | None = None,
        publisher: Callable[[ObservationEvent], None] | None = None,
    ) -> None:
        self.mapper = mapper or ObservationMapper()
        self.publisher = publisher
        self.state: WorldState | None = None

    def process(
        self,
        observation: MultiEntityObservation,
        *,
        map_id: str | None = None,
        tick: int | None = None,
        correlation_id: str | None = None,
    ) -> ObservationEvent:
        state = self.mapper.update(
            self.state,
            observation,
            map_id=map_id,
            tick=tick,
        )
        self.state = state
        event = ObservationEvent(
            correlation_id=correlation_id or str(uuid4()),
            tick=state.tick,
            observed_at=datetime.now(timezone.utc).isoformat(),
            observation=observation.to_dict(),
            world_state=state.to_dict(),
        )
        if self.publisher is not None:
            self.publisher(event)
        return event

    def snapshot(self) -> WorldState | None:
        return None if self.state is None else self.state.copy()
