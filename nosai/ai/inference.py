"""Read-only, deterministic AI inference boundary (G3.19)."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from math import isfinite


@dataclass(frozen=True)
class InferenceResult:
    schema_version: str
    session_id: str
    score: float
    confidence: float
    input_digest: str


class ReadOnlyInference:
    """Produces bounded scores from validated features; never emits actions."""

    SCHEMA_VERSION = "g3.19.v1"

    def predict(self, session_id: str, features: dict[str, float]) -> InferenceResult:
        if not session_id.strip():
            raise ValueError("session_id must be non-empty")
        if not features:
            raise ValueError("features must be non-empty")
        clean: dict[str, float] = {}
        for key, value in features.items():
            if not isinstance(key, str) or not key.strip():
                continue
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                continue
            if isfinite(numeric):
                clean[key] = numeric
        if not clean:
            raise ValueError("features contain no finite numeric values")
        canonical = json.dumps(clean, sort_keys=True, separators=(",", ":"))
        digest = sha256(canonical.encode()).hexdigest()
        raw = sum(clean.values()) / len(clean)
        score = max(0.0, min(1.0, raw / 100.0))
        confidence = min(1.0, len(clean) / 5.0)
        return InferenceResult(self.SCHEMA_VERSION, session_id, score, confidence, digest)
