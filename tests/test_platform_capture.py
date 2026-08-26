from types import SimpleNamespace

import pytest

from app.platform.capture import DxcamCapture


def test_dxcam_requires_windows(monkeypatch):
    monkeypatch.setattr("os.name", "posix")
    with pytest.raises(RuntimeError, match="only supported on Windows"):
        DxcamCapture().start()


def test_dxcam_adapter_wraps_latest_frame(monkeypatch):
    class FakeFrame:
        shape = (720, 1280, 3)

    class FakeCamera:
        def start(self, **kwargs):
            self.kwargs = kwargs

        def stop(self):
            pass

        def get_latest_frame(self):
            return FakeFrame()

    fake_dxcam = SimpleNamespace(create=lambda **kwargs: FakeCamera())
    monkeypatch.setattr("os.name", "nt")
    monkeypatch.setitem(__import__("sys").modules, "dxcam", fake_dxcam)

    capture = DxcamCapture(region=(0, 0, 1280, 720), target_fps=30)
    capture.start()
    frame = capture.get_latest()

    assert frame is not None
    assert frame.backend == "dxcam"
    assert (frame.width, frame.height) == (1280, 720)
    assert frame.frame_id == 1
    capture.stop()
