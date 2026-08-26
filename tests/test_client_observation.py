from app.client.observation import ObservationFrame, build_observation


def test_observation_frame_is_normalized_and_immutable() -> None:
    frame = build_observation(
        pid=123,
        window={"left": 10, "top": 20, "width": 800, "height": 600},
        image=b"pixels",
        width=800,
        height=600,
        metadata={"observation_only": True},
        timestamp_ns=42,
    )
    assert isinstance(frame, ObservationFrame)
    assert frame.timestamp_ns == 42
    assert frame.pid == 123
    assert frame.window["width"] == 800
    assert frame.image == b"pixels"
    assert frame.metadata["observation_only"] is True


def test_observation_serialization_excludes_pixels_by_default() -> None:
    frame = build_observation(pid=1, window={}, image=b"secret")
    payload = frame.as_dict()
    assert "image_bytes" not in payload
    assert payload["pid"] == 1


def test_observation_serialization_can_include_pixels_explicitly() -> None:
    frame = build_observation(pid=1, window={}, image=b"pixels")
    assert frame.as_dict(include_image=True)["image_bytes"] == b"pixels"
