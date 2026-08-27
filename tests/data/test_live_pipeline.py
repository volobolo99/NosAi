from datetime import datetime, timezone

from nosai.data.live_dataset import LiveDatasetRecorder
from nosai.data.live_pipeline import LiveObservationPipeline


def test_live_observation_pipeline_accepts_and_records_snapshot():
    pipeline = LiveObservationPipeline(LiveDatasetRecorder())
    record = pipeline.ingest("live-1", {"map": "real", "hp": 100}, observed_at=datetime(2026, 8, 27, 16, 0, tzinfo=timezone.utc))
    assert record is not None
    assert pipeline.stats().accepted == 1
    assert pipeline.stats().rejected == 0


def test_live_observation_pipeline_rejects_invalid_snapshot_without_action():
    pipeline = LiveObservationPipeline(LiveDatasetRecorder())
    assert pipeline.ingest("live-1", {}) is None
    assert pipeline.stats().rejected == 1
    assert pipeline.records() == ()
