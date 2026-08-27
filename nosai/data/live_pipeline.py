"""Bridge read-only live observations into the validated AI dataset recorder."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .live_dataset import DatasetRecord, LiveDatasetRecorder


@dataclass(frozen=True)
class PipelineStats:
    accepted: int
    rejected: int


class LiveObservationPipeline:
    """Observation-only adapter; it consumes snapshots and never emits actions."""

    def __init__(self, recorder: LiveDatasetRecorder) -> None:
        self._recorder = recorder
        self._accepted = 0
        self._rejected = 0

    def ingest(self, session_id: str, snapshot: dict[str, object], *, observed_at: datetime | None = None) -> DatasetRecord | None:
        try:
            record = self._recorder.append(session_id, snapshot, observed_at=observed_at)
        except (TypeError, ValueError):
            self._rejected += 1
            return None
        self._accepted += 1
        return record

    def stats(self) -> PipelineStats:
        return PipelineStats(self._accepted, self._rejected)

    def records(self) -> tuple[DatasetRecord, ...]:
        return self._recorder.records()
