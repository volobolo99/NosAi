"""Read-only Windows frame source for the NosTale client.

This adapter intentionally captures pixels only. It performs no input injection,
memory access, patching, or gameplay action transport.
"""
from __future__ import annotations

from dataclasses import dataclass
from time import time_ns
from typing import Protocol

from .perception import Frame


class WindowCaptureBackend(Protocol):
    """Minimal backend boundary; platform-specific code stays outside perception."""

    def capture(self, window_handle: int) -> tuple[int, int, bytes]:
        """Return width, height and packed pixel bytes for one window capture."""


@dataclass(frozen=True)
class WindowsWindowTarget:
    """Explicitly selected client target, allowing deterministic manual selection."""

    hwnd: int
    pid: int | None = None
    title: str | None = None


class WindowsFrameSource:
    """Capture a selected Windows window through an injected read-only backend."""

    def __init__(self, target: WindowsWindowTarget, backend: WindowCaptureBackend) -> None:
        if target.hwnd <= 0:
            raise ValueError("window handle must be positive")
        self._target = target
        self._backend = backend
        self._sequence = 0

    @property
    def target(self) -> WindowsWindowTarget:
        return self._target

    def capture(self) -> Frame:
        width, height, pixels = self._backend.capture(self._target.hwnd)
        if width <= 0 or height <= 0:
            raise ValueError("captured frame dimensions must be positive")
        if not isinstance(pixels, bytes):
            raise TypeError("capture backend must return bytes")
        self._sequence += 1
        timestamp_ms = time_ns() // 1_000_000
        return Frame(
            frame_id=f"win:{self._target.hwnd}:{self._sequence}",
            timestamp_ms=timestamp_ms,
            width=width,
            height=height,
            pixels=pixels,
            source="windows.window.capture",
        )
