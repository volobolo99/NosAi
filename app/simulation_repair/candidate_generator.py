"""Candidate generation from researched evidence.

This layer creates *proposals*, not patches. Every proposal keeps provenance
and must be evaluated by the sandbox before it can be considered viable.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Iterable

from .research import ResearchHit


@dataclass(frozen=True)
class CandidateProposal:
    candidate_id: str
    strategy: str
    description: str
    evidence_urls: tuple[str, ...]
    source_repositories: tuple[str, ...]


def generate_candidates(error_type: str, message: str, hits: Iterable[ResearchHit], *, limit: int = 8) -> list[CandidateProposal]:
    """Create diverse, traceable proposals from research evidence.

    The generator intentionally does not synthesize executable source code.
    A later, explicitly configured code-generation provider may produce a patch
    proposal, which still requires sandbox evaluation and human approval.
    """
    unique: dict[str, ResearchHit] = {}
    for hit in hits:
        unique.setdefault(hit.url, hit)

    proposals: list[CandidateProposal] = []
    strategies = (
        "dependency_or_environment",
        "api_or_contract",
        "error_handling_or_retry",
        "algorithm_or_control_flow",
    )
    for index, hit in enumerate(unique.values()):
        if index >= max(1, min(limit, 16)):
            break
        digest = sha256(f"{error_type}\n{message}\n{hit.url}".encode()).hexdigest()[:12]
        strategy = strategies[index % len(strategies)]
        proposals.append(
            CandidateProposal(
                candidate_id=f"cand-{digest}",
                strategy=strategy,
                description=f"Research-backed proposal for {error_type} using evidence from {hit.title}",
                evidence_urls=(hit.url,),
                source_repositories=((hit.repository,) if hit.repository else ()),
            )
        )
    return proposals
