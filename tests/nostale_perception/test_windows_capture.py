from __future__ import annotations

import pytest

from app.nostale_perception.windows_capture import WindowsFrameSource, WindowsWindowTarget


class FakeBackend:
    def __init__(self, payload: bytes = b"pixels") -> None:
        self.payload = payload
        self.handles: list[int] = []

    def capture(self, window_handle: int) -> tuple[int, int, bytes]:
        self.handles.append(window_handle)
        return 2, 2, self.payload


def test_capture_is_read_only_and_preserves_selected_target() -> None:
    backend = FakeBackend()
    target = WindowsWindowTarget(hwnd=1234, pid=55, title="NosTale")
    source = WindowsFrameSource(target, backend)

    frame = source.capture()

    assert backend.handles == [1234]
    assert frame.width == 2
    assert frame.height == 2
    assert frame.pixels == b"pixels"
    assert frame.source == "windows.window.capture"
    assert frame.frame_id == "win:1234:1"
    assert source.target == target


def test_invalid_window_handle_is_rejected() -> None:
    with pytest.raises(ValueError, match="window handle"):
        WindowsFrameSource(WindowsWindowTarget(hwnd=0), FakeBackend())


def test_invalid_capture_dimensions_are_rejected() -> None:
    class BadBackend(FakeBackend):
        def capture(self, window_handle: int) -> tuple[int, int, bytes]:
            return 0, 2, b"pixels"

    source = WindowsFrameSource(WindowsWindowTarget(hwnd=1), BadBackend())
    with pytest.raises(ValueError, match="dimensions"):
        source.capture()


def test_non_bytes_payload_is_rejected() -> None:
    class BadBackend(FakeBackend):
        def capture(self, window_handle: int) -> tuple[int, int, bytes]:
            return 2, 2, "not-bytes"  # type: ignore[return-value]

    source = WindowsFrameSource(WindowsWindowTarget(hwnd=1), BadBackend())
    with pytest.raises(TypeError, match="bytes"):
        source.capture()
