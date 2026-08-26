from app.client.observation import build_observation
from app.client.perception import perceive


def test_perception_reports_missing_frame_without_false_detection() -> None:
    result = perceive(build_observation(pid=1, window={}, timestamp_ns=7))
    assert result.frame_available is False
    assert result.quality == "non_disponibile"
    assert result.detections == ()
    assert result.confidence == 0.0


def test_perception_reports_acquired_frame() -> None:
    frame = build_observation(pid=1, window={}, image=b"pixels", width=100, height=80, timestamp_ns=9)
    result = perceive(frame)
    assert result.frame_available is True
    assert result.quality == "acquisito"
    assert result.frame_width == 100
    assert result.frame_height == 80
    assert result.detections == ()
