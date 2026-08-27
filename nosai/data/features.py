"""Deterministic AI-ready feature extraction from observation records (G3.17)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite


SCHEMA_VERSION = "g3.17.v1"


@dataclass(frozen=True)
class FeatureVector:
    schema_version: str
    session_id: str
    observed_at: str
    values: dict[str, float]
    quality: float


class ObservationFeatureExtractor:
    """Extracts bounded numeric features without making runtime decisions."""

    _NUMERIC_KEYS = ("hp", "mp", "x", "y", "level")

    def extract(self, session_id: str, observed_at: str, payload: dict[str, object]) -> FeatureVector:
        if not session_id.strip():
            raise ValueError("session_id must be non-empty")
        if not observed_at.strip():
            raise ValueError("observed_at must be non-empty")
        datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
        if not isinstance(payload, dict) or not payload:
            raise ValueError("payload must be a non-empty mapping")

        values: dict[str, float] = {}
        for key in self._NUMERIC_KEYS:
            value = payload.get(key)
            if isinstance(value, bool):
                continue
            try:
                numeric = float(value) if value is not None else None
            except (TypeError, ValueError):
                numeric = None
            if numeric is not None and isfinite(numeric):
                values[key] = numeric

        quality = len(values) / len(self._NUMERIC_KEYS)
        return FeatureVector(SCHEMA_VERSION, session_id, observed_at, values, quality)
