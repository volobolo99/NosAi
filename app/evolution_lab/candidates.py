"""Candidate and multi-candidate composition contracts.

Composition is deliberately deterministic and provenance-preserving. It does
not execute or auto-promote generated code; downstream validation gates decide.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256


@dataclass(frozen=True, slots=True)
class Candidate:
    candidate_id: str
    source_finding_ids: tuple[str, ...]
    patch: str
    rationale: str
    score: float = 0.0


@dataclass(frozen=True, slots=True)
class CandidateEnsemble:
    ensemble_id: str
    candidate_ids: tuple[str, ...]
    composite_patch: str
    provenance: tuple[str, ...]


def compose_ensemble(candidates: tuple[Candidate, ...] | list[Candidate]) -> CandidateEnsemble:
    ordered = sorted(candidates, key=lambda c: (-c.score, c.candidate_id))
    if not ordered:
        raise ValueError("cannot compose an empty candidate set")
    selected = tuple(ordered)
    composite = "\n\n".join(c.patch.rstrip() for c in selected if c.patch.strip())
    identity = "|".join(c.candidate_id for c in selected)
    ensemble_id = "ens-" + sha256(identity.encode("utf-8")).hexdigest()[:16]
    provenance = tuple(fid for c in selected for fid in c.source_finding_ids)
    return CandidateEnsemble(ensemble_id, tuple(c.candidate_id for c in selected), composite, provenance)
