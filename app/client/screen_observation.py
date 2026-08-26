"""Read-only screen capture for the visible NosTale window.

This module never injects input and never reads or writes process memory. It
captures only the pixels already visible on the user's screen.
"""
from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Any

from .nostale_windows import WindowInfo


@dataclass(frozen=True)
class ScreenFrame:
    """JPEG-encoded observation of a visible game window."""

    image_bytes: bytes
    width: int
    height: int
    content_type: str = "image/jpeg"


def capture_window(window: WindowInfo) -> ScreenFrame:
    """Capture the visible window rectangle using Pillow on Windows."""
    if window.width <= 0 or window.height <= 0:
        raise ValueError("window dimensions must be positive")
    try:
        from PIL import ImageGrab
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise RuntimeError("Pillow is required for screen observation") from exc

    image = ImageGrab.grab(bbox=(window.left, window.top, window.right, window.bottom), all_screens=True)
    output = BytesIO()
    image.convert("RGB").save(output, format="JPEG", quality=82, optimize=True)
    return ScreenFrame(output.getvalue(), image.width, image.height)


def capture_largest_nostale_window(adapter: Any) -> ScreenFrame:
    """Capture the largest visible window discovered by a Windows adapter."""
    windows = adapter._find_windows()  # private helper is local to the adapter boundary
    if not windows:
        raise RuntimeError("no visible NosTale window found")
    window = max(windows, key=lambda item: (item.area, item.width, item.height))
    return capture_window(window)
