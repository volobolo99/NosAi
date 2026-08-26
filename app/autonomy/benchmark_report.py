"""Structured reporting for scenario benchmark results."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .shadow_compare import ShadowComparison


@dataclass(frozen=True)
class ScenarioBenchmarkReport:
    total: int
    valid_states: int
    invalid_states: int
    agreements: int
    ai_valid: int
    ai_allowed: int

    @classmethod
    def from_comparisons(cls, comparisons: Iterable[ShadowComparison]) -> "ScenarioBenchmarkReport":
        items = tuple(comparisons)
        return cls(
            total=len(items),
            valid_states=sum(item.deterministic.state_valid for item in items),
            invalid_states=sum(not item.deterministic.state_valid for item in items),
            agreements=sum(item.record.agreement for item in items),
            ai_valid=sum(item.record.ai_valid for item in items),
            ai_allowed=sum(item.record.ai_allowed for item in items),
        )

    @property
    def agreement_rate(self) -> float:
        return self.agreements / self.total if self.total else 0.0

    @property
    def ai_valid_rate(self) -> float:
        return self.ai_valid / self.total if self.total else 0.0

    @property
    def ai_allowed_rate(self) -> float:
        return self.ai_allowed / self.total if self.total else 0.0
