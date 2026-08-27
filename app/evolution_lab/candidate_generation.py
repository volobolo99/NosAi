"""Deterministic candidate generation from research findings.

This layer creates reviewable proposals only. It never executes generated code
and never promotes a candidate; downstream gates remain mandatory.
"""
from __future__ import annotations

from hashlib import sha256

from .candidates import Candidate
from .research import ResearchFinding


def generate_candidates(findings: tuple[ResearchFinding, ...] | list[ResearchFinding]) -> tuple[Candidate, ...]:
    candidates: list[Candidate] = []
    for finding in findings:
        identity = f"{finding.finding_id}|{finding.source}|{finding.title}"
        candidate_id = "cand-" + sha256(identity.encode("utf-8")).hexdigest()[:16]
        patch = finding.summary.strip()
        candidates.append(
            Candidate(
                candidate_id=candidate_id,
                source_finding_ids=(finding.finding_id,),
                patch=patch,
                rationale=f"Proposal derived from research finding {finding.finding_id}.",
                score=finding.score,
            )
        )
    return tuple(candidates)
