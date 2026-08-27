"""Provider-neutral online research adapter boundary.

The core stays offline-first: concrete network clients live outside this module.
A provider may return findings, but callers must preserve provenance and pass
all generated candidates through the simulation/regression gates.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .research import ResearchFinding, ResearchResult, rank_findings


class ResearchProvider(Protocol):
    name: str

    def search(self, query: str, *, limit: int = 10) -> ResearchResult: ...


@dataclass(frozen=True, slots=True)
class AggregatedResearch:
    query: str
    findings: tuple[ResearchFinding, ...]
    providers: tuple[str, ...]


def aggregate_research(query: str, providers: list[ResearchProvider], *, limit: int = 10) -> AggregatedResearch:
    if limit < 1:
        raise ValueError("limit must be positive")
    findings: list[ResearchFinding] = []
    names: list[str] = []
    for provider in providers:
        result = provider.search(query, limit=limit)
        findings.extend(result.findings)
        names.append(provider.name)
    ranked = rank_findings(findings)
    return AggregatedResearch(query, ranked[:limit], tuple(dict.fromkeys(names)))
