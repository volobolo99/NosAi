from __future__ import annotations

from app.guardai.telemetry_synchronizer import GuardAiTelemetrySynchronizer


def test_pairs_closest_pts_within_tolerance() -> None:
    sync = GuardAiTelemetrySynchronizer(tolerance_us=5_000)
    sync.add_telemetry(1_000_000, {"hp": 100})
    sync.add_telemetry(1_006_000, {"hp": 90})

    pair = sync.pair_frame(7, 1_004_000)

    assert pair is not None
    assert pair.frame_id == 7
    assert pair.telemetry_pts_us == 1_006_000
    assert pair.skew_us == 2_000
    assert pair.telemetry_payload == {"hp": 90}


def test_returns_none_when_outside_tolerance() -> None:
    sync = GuardAiTelemetrySynchronizer(tolerance_us=1_000)
    sync.add_telemetry(1_000_000, {"hp": 100})

    assert sync.pair_frame(1, 1_005_000) is None


def test_tie_prefers_older_pts() -> None:
    sync = GuardAiTelemetrySynchronizer(tolerance_us=10_000)
    sync.add_telemetry(900_000, {"source": "old"})
    sync.add_telemetry(1_100_000, {"source": "new"})

    pair = sync.pair_frame(2, 1_000_000)

    assert pair is not None
    assert pair.telemetry_pts_us == 900_000


def test_telemetry_is_consumed_after_pairing() -> None:
    sync = GuardAiTelemetrySynchronizer(tolerance_us=5_000)
    sync.add_telemetry(1_000_000, {"x": 1})

    assert sync.pair_frame(1, 1_000_000) is not None
    assert sync.pair_frame(2, 1_000_000) is None


def test_buffer_is_bounded() -> None:
    sync = GuardAiTelemetrySynchronizer(max_buffer_size=2)
    sync.add_telemetry(1, {"v": 1})
    sync.add_telemetry(2, {"v": 2})
    sync.add_telemetry(3, {"v": 3})

    assert len(sync) == 2
    assert sync.pair_frame(1, 1) is None
