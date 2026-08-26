"""Read-only HUD OCR for the real Windows NosTale frame.

The parser produces observations only. It never sends input or changes client state.
OCR is optional and loaded lazily so CI remains platform independent.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

from .windows_perception import Frame


@dataclass(frozen=True)
class HudObservation:
    text: str
    hp: int | None = None
    mp: int | None = None
    level: int | None = None
    source: str = "ocr"
    observation_only: bool = True


_INT = re.compile(r"\b(\d{1,7})\b")


def _first_int(text: str, patterns: tuple[str, ...]) -> int | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
    return None


class WindowsHudOcr:
    """OCR adapter. Requires the optional pytesseract package at runtime."""

    def extract(self, frame: Frame) -> HudObservation:
        try:
            import cv2
            import numpy as np
            import pytesseract
        except ImportError as exc:
            raise RuntimeError("OCR requires the optional 'ocr' dependencies") from exc

        image = cv2.imdecode(np.frombuffer(frame.png, dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("invalid PNG frame")
        text = pytesseract.image_to_string(image, config="--psm 11")
        return HudObservation(
            text=text.strip(),
            hp=_first_int(text, (r"(?:HP|PV)\s*[:=]?\s*(\d+)",)),
            mp=_first_int(text, (r"(?:MP|PM)\s*[:=]?\s*(\d+)",)),
            level=_first_int(text, (r"(?:LV|LEVEL|LIV)\s*[:=]?\s*(\d+)",)),
        )
