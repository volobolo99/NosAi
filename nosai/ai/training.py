"""Deterministic offline training foundation for G3.22."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class DatasetSplit:
    train: tuple[dict[str, object], ...]
    validation: tuple[dict[str, object], ...]
    test: tuple[dict[str, object], ...]


@dataclass(frozen=True)
class TrainingReport:
    samples: int
    train_samples: int
    validation_samples: int
    test_samples: int
    baseline_score: float
    dataset_digest: str


def split_dataset(samples: list[dict[str, object]], train_ratio: float = 0.8, validation_ratio: float = 0.1) -> DatasetSplit:
    if not samples:
        raise ValueError("samples must be non-empty")
    if not 0 < train_ratio < 1 or not 0 <= validation_ratio < 1 or train_ratio + validation_ratio >= 1:
        raise ValueError("invalid split ratios")
    ordered = sorted(samples, key=lambda item: json.dumps(item, sort_keys=True, default=str))
    n = len(ordered)
    train_end = max(1, int(n * train_ratio))
    validation_end = min(n - 1, train_end + int(n * validation_ratio))
    return DatasetSplit(tuple(ordered[:train_end]), tuple(ordered[train_end:validation_end]), tuple(ordered[validation_end:]))


def train_baseline(samples: list[dict[str, object]]) -> TrainingReport:
    split = split_dataset(samples)
    canonical = json.dumps(samples, sort_keys=True, separators=(",", ":"), default=str)
    scores = [float(x["score"]) for x in split.train if isinstance(x.get("score"), (int, float))]
    baseline = sum(scores) / len(scores) if scores else 0.0
    return TrainingReport(
        samples=len(samples), train_samples=len(split.train),
        validation_samples=len(split.validation), test_samples=len(split.test),
        baseline_score=max(0.0, min(1.0, baseline)),
        dataset_digest=sha256(canonical.encode()).hexdigest(),
    )
