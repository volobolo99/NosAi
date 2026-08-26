"""Embedding contracts for the NosAi knowledge engine.

The baseline embedding is deterministic and dependency-free so retrieval
benchmarks can run in CI without network access or an API key. Production
providers can implement the same protocol later.
"""
from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol, Sequence

_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{1,}")


class EmbeddingProvider(Protocol):
    name: str
    dimensions: int

    def embed(self, text: str) -> Sequence[float]: ...


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right) or not left:
        raise ValueError("vectors must have equal, non-zero dimensions")
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


class HashEmbeddingProvider:
    """Deterministic hashing baseline, not a semantic production model."""

    name = "hash-baseline"

    def __init__(self, dimensions: int = 128) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions must be positive")
        self.dimensions = dimensions

    def embed(self, text: str) -> Sequence[float]:
        vector = [0.0] * self.dimensions
        tokens = _TOKEN_RE.findall(text.lower())
        if not tokens:
            return vector
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] & 1 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(x * x for x in vector))
        return tuple(x / norm for x in vector) if norm else tuple(vector)
