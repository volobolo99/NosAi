"""Observation-only HUD/OCR normalization into WorldState fields."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class HudValue:
    value: str
    confidence: float
    source: str = "ocr"

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("HUD confidence must be between 0 and 1")


class HudStateExtractor:
    """Normalize OCR/template HUD outputs without performing client I/O."""

    FIELD_ALIASES = {
        "hp": "hp",
        "health": "hp",
        "mp": "mp",
        "mana": "mp",
        "level": "level",
        "lv": "level",
        "gold": "gold",
    }

    def extract(self, values: Mapping[str, HudValue], *, min_confidence: float = 0.70) -> dict[str, object]:
        if not 0.0 <= min_confidence <= 1.0:
            raise ValueError("min_confidence must be between 0 and 1")
        state: dict[str, object] = {}
        confidence: dict[str, float] = {}
        provenance: dict[str, str] = {}
        for raw_key, item in values.items():
            if item.confidence < min_confidence:
                continue
            key = self.FIELD_ALIASES.get(raw_key.lower())
            if key is None:
                continue
            state[key] = self._coerce(item.value)
            confidence[key] = item.confidence
            provenance[key] = item.source
        if confidence:
            state["hud_confidence"] = confidence
            state["hud_provenance"] = provenance
        return state

    @staticmethod
    def _coerce(value: str) -> object:
        normalized = value.replace(".", "").replace(",", "").strip()
        if normalized.isdigit():
            return int(normalized)
        return value.strip()
