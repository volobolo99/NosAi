"""Backend-neutral frame capture primitives for Windows perception."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any, Protocol


@dataclass(frozen=True)
class CapturedFrame:
    frame_id: int
    timestamp: float
    width: int
    height: int
    backend: str
    image: Any


class FrameCapture(Protocol):
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def get_latest(self) -> CapturedFrame | None: ...


class DxcamCapture:
    """Optional DXcam adapter; importing NosAi must not require DXcam."""

    def __init__(self, region: tuple[int, int, int, int] | None = None, target_fps: int = 30) -> None:
        self.region = region
        self.target_fps = target_fps
        self._camera: Any = None
        self._frame_id = 0

    def start(self) -> None:
        if self._camera is not None:
            return
        if __import__("os").name != "nt":
            raise RuntimeError("DXcam capture is only supported on Windows")
        try:
            import dxcam
        except ImportError as exc:
            raise RuntimeError("DXcam is not installed; install the Windows perception extra") from exc
        self._camera = dxcam.create(output_idx=0, output_color="BGR")
        self._camera.start(region=self.region, target_fps=self.target_fps, video_mode=False)

    def stop(self) -> None:
        if self._camera is not None:
            self._camera.stop()
            self._camera = None

    def get_latest(self) -> CapturedFrame | None:
        if self._camera is None:
            raise RuntimeError("capture is not started")
        image = self._camera.get_latest_frame()
        if image is None:
            return None
        self._frame_id += 1
        height, width = image.shape[:2]
        return CapturedFrame(
            frame_id=self._frame_id,
            timestamp=perf_counter(),
            width=width,
            height=height,
            backend="dxcam",
            image=image,
        )
