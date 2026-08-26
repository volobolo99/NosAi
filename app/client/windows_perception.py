"""Read-only visual perception for a real Windows NosTale window.

This module deliberately performs screen capture only. It does not inject
input, patch process memory, or execute game actions. OCR/object detection can
be layered on top of the returned frame without changing the safety boundary.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from .nostale_windows import NosTaleClientError, WindowsNosTaleAdapter
from .multi_entity import MultiEntityObservation, MultiEntityRecognizer


@dataclass(frozen=True)
class Frame:
    png: bytes
    width: int
    height: int
    source: str = "windows_screen_capture"
    observation_only: bool = True


class WindowsNosTalePerception:
    """Capture and optionally recognize the visible NosTale window read-only."""

    def __init__(self, adapter: WindowsNosTaleAdapter | None = None) -> None:
        self.adapter = adapter or WindowsNosTaleAdapter()

    def capture(self) -> Frame:
        if os.name != "nt":
            raise NosTaleClientError("Windows visual perception requires Windows")
        try:
            import cv2
            import mss
            import numpy as np
        except ImportError as exc:
            raise NosTaleClientError(
                "Visual perception requires the 'vision' optional dependencies"
            ) from exc

        state = self.adapter.read_state()
        rect = state.payload["window_rect"]
        monitor = {
            "left": int(rect["left"]),
            "top": int(rect["top"]),
            "width": int(rect["width"]),
            "height": int(rect["height"]),
        }
        if monitor["width"] <= 0 or monitor["height"] <= 0:
            raise NosTaleClientError("NosTale window has an invalid capture rectangle")

        with mss.mss() as sct:
            raw = np.asarray(sct.grab(monitor))
        bgr = cv2.cvtColor(raw, cv2.COLOR_BGRA2BGR)
        ok, encoded = cv2.imencode(".png", bgr)
        if not ok:
            raise NosTaleClientError("cannot encode NosTale screenshot")
        return Frame(
            png=encoded.tobytes(),
            width=int(bgr.shape[1]),
            height=int(bgr.shape[0]),
        )

    def capture_and_recognize(
        self, recognizer: MultiEntityRecognizer
    ) -> tuple[Frame, MultiEntityObservation]:
        """Capture one real frame and return observation-only entity results."""
        frame = self.capture()
        try:
            import cv2
            import numpy as np
        except ImportError as exc:
            raise NosTaleClientError(
                "Visual recognition requires the 'vision' optional dependencies"
            ) from exc
        image = cv2.imdecode(np.frombuffer(frame.png, dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            raise NosTaleClientError("cannot decode captured NosTale screenshot")
        return frame, recognizer.recognize(image)
