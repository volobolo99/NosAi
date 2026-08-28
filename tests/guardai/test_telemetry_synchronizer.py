import pytest

from app.guardai.telemetry_synchronizer import (
    FrameTelemetryPair,
    GuardAiTelemetrySynchronizer,
)


def test_synchronizer_exact_match() -> None:
    synchronizer = GuardAiTelemetrySynchronizer()
    synchronizer.push_telemetry(
        frame_id=101, pts_us=1000000, payload={"player_hp": 100}
    )

    pair = synchronizer.match_frame(
        frame_id=101, video_pts_us=1002000, tolerance_window_us=16000
    )

    assert pair is not None
    assert isinstance(pair, FrameTelemetryPair)
    assert pair.frame_id == 101
    assert pair.video_pts_us == 1002000
    assert pair.telemetry_pts_us == 1000000
    assert pair.skew_us == 2000
    assert pair.telemetry_payload == {"player_hp": 100}
    assert synchronizer.last_skew_us == 2000
    assert synchronizer.total_matched == 1


def test_synchronizer_out_of_order_reorder_recovery() -> None:
    synchronizer = GuardAiTelemetrySynchronizer()
    synchronizer.push_telemetry(
        frame_id=102, pts_us=1016000, payload={"event": "mob_hit"}
    )
    synchronizer.push_telemetry(
        frame_id=101, pts_us=1000000, payload={"event": "walk"}
    )

    pair_101 = synchronizer.match_frame(
        frame_id=101, video_pts_us=1001000, tolerance_window_us=16000
    )
    assert pair_101 is not None
    assert pair_101.frame_id == 101
    assert pair_101.skew_us == 1000

    pair_102 = synchronizer.match_frame(
        frame_id=102, video_pts_us=1017000, tolerance_window_us=16000
    )
    assert pair_102 is not None
    assert pair_102.frame_id == 102
    assert pair_102.skew_us == 1000


def test_synchronizer_tolerance_exceeded() -> None:
    synchronizer = GuardAiTelemetrySynchronizer()
    synchronizer.push_telemetry(
        frame_id=200, pts_us=1000000, payload={"target": "boss"}
    )

    pair = synchronizer.match_frame(
        frame_id=200, video_pts_us=1030000, tolerance_window_us=16000
    )

    assert pair is None
    assert synchronizer.last_skew_us == 30000


def test_synchronizer_malformed_fail_closed() -> None:
    synchronizer = GuardAiTelemetrySynchronizer()

    synchronizer.push_telemetry(
        frame_id="invalid", pts_us=1000, payload={"data": 1}  # type: ignore[arg-type]
    )
    synchronizer.push_telemetry(
        frame_id=1, pts_us=-500, payload={"data": 1}
    )

    assert synchronizer.total_dropped == 2
    assert synchronizer.match_frame(frame_id=1, video_pts_us=1000) is None


def test_synchronizer_buffer_eviction() -> None:
    synchronizer = GuardAiTelemetrySynchronizer(max_buffer_size=2)
    synchronizer.push_telemetry(frame_id=1, pts_us=1000, payload={"id": 1})
    synchronizer.push_telemetry(frame_id=2, pts_us=2000, payload={"id": 2})
    synchronizer.push_telemetry(
        frame_id=3, pts_us=3000, payload={"id": 3}
    )

    assert synchronizer.total_dropped == 1
    assert synchronizer.match_frame(frame_id=1, video_pts_us=1000) is None
    assert synchronizer.match_frame(frame_id=2, video_pts_us=2000) is not None
