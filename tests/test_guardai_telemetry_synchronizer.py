from __future__ import annotations

from app.guardai.telemetry_synchronizer import GuardAiTelemetrySynchronizer


def test_exact_frame_id_pair_within_tolerance() -> None:
    sync = GuardAiTelemetrySynchronizer()
    sync.push_telemetry(7, 1_000_000, {"hp": 100})
    pair = sync.match_frame(7, 1_004_000)
    assert pair is not None
    assert pair.frame_id == 7
    assert pair.telemetry_pts_us == 1_000_000
    assert pair.skew_us == 4_000
    assert sync.total_matched == 1


def test_nearest_pts_fallback_handles_reordering() -> None:
    sync = GuardAiTelemetrySynchronizer()
    sync.push_telemetry(10, 1_000_000, {"source": "old"})
    sync.push_telemetry(11, 1_006_000, {"source": "new"})
    pair = sync.match_frame(99, 1_004_000)
    assert pair is not None
    assert pair.telemetry_pts_us == 1_006_000
    assert pair.skew_us == 2_000


def test_tie_prefers_lower_pts() -> None:
    sync = GuardAiTelemetrySynchronizer()
    sync.push_telemetry(1, 900_000, {"source": "old"})
    sync.push_telemetry(2, 1_100_000, {"source": "new"})
    pair = sync.match_frame(3, 1_000_000)
    assert pair is not None
    assert pair.telemetry_pts_us == 900_000


def test_outside_tolerance_is_dropped_without_exception() -> None:
    sync = GuardAiTelemetrySynchronizer()
    sync.push_telemetry(1, 1_000_000, {"hp": 100})
    assert sync.match_frame(1, 1_020_001, tolerance_window_us=16_000) is None
    assert sync.total_matched == 0
    assert sync.total_dropped == 1


def test_malformed_and_negative_telemetry_are_dropped_fail_closed() -> None:
    sync = GuardAiTelemetrySynchronizer()
    sync.push_telemetry("bad", 1, {})  # type: ignore[arg-type]
    sync.push_telemetry(1, -1, {})
    sync.push_telemetry(2, 2, [])  # type: ignore[arg-type]
    assert sync.total_dropped == 3


def test_duplicate_frame_id_is_dropped() -> None:
    sync = GuardAiTelemetrySynchronizer()
    sync.push_telemetry(1, 100, {"v": 1})
    sync.push_telemetry(1, 101, {"v": 2})
    assert sync.total_dropped == 1
    assert sync.match_frame(1, 100) is not None


def test_buffer_is_bounded() -> None:
    sync = GuardAiTelemetrySynchronizer(max_buffer_size=2)
    sync.push_telemetry(1, 1, {"v": 1})
    sync.push_telemetry(2, 2, {"v": 2})
    sync.push_telemetry(3, 3, {"v": 3})
    assert sync.total_dropped == 1
    assert sync.match_frame(1, 1, tolerance_window_us=0) is None


def test_invalid_match_arguments_fail_closed() -> None:
    sync = GuardAiTelemetrySynchronizer()
    assert sync.match_frame(-1, 1) is None
    assert sync.match_frame(1, -1) is None
    assert sync.match_frame(1, 1, -1) is None
