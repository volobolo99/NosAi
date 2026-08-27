"""Provider-neutral research findings and deterministic ranking.

Network access belongs to adapters outside this core. Findings retain source
provenance and are never treated as trusted code merely because they rank high.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ResearchFinding:
    finding_id: str
    source: str
    title: str
    summary: str
    url: str | None = None
    relevance: float = 0.0
    reliability: float = 0.0
    freshness: float = 0.0

    @property
    def score(self) -> float:
        return 0.5 * self.relevance + 0.35 * self.reliability + 0.15 * self.freshness


@dataclass(frozen=True, slots=True)
class ResearchResult:
    query: str
    findings: tuple[ResearchFinding, ...]


def rank_findings(findings: tuple[ResearchFinding, ...] | list[ResearchFinding]) -> tuple[ResearchFinding, ...]:
    return tuple(sorted(findings, key=lambda item: (-item.score, item.source, item.finding_id)))
