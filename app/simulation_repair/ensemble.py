"""Evidence-driven synthesis of multiple simulated repair candidates."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import CandidateResult


@dataclass(slots=True)
class EnsembleResult:
    status: str
    selected_candidate_ids: list[str]
    compatible_candidate_ids: list[str]
    composite_plan: list[str]
    conflicts: list[str]
    score: float


def _candidate_score(candidate: CandidateResult) -> float:
    checks = list(candidate.checks.values())
    passed = sum(v == "PASS" for v in checks)
    failed = sum(v == "FAIL" for v in checks)
    evidence_bonus = min(len(candidate.evidence), 5) * 0.05
    return max(0.0, (passed - failed * 0.5) + evidence_bonus)


def synthesize(candidates: Iterable[CandidateResult]) -> EnsembleResult:
    """Build a composite proposal from compatible PASS candidates.

    This never writes production code. Explicit ``CONFLICT:<group>`` markers
    prevent incompatible candidates from being silently merged.
    """
    items = list(candidates)
    passing = [c for c in items if c.status == "PASS"]
    if not passing:
        return EnsembleResult("NO_PASS", [], [], [], [], 0.0)

    passing.sort(key=_candidate_score, reverse=True)
    groups: dict[str, list[str]] = {}
    for candidate in passing:
        for note in candidate.notes:
            if note.startswith("CONFLICT:"):
                groups.setdefault(note.split(":", 1)[1].strip(), []).append(candidate.candidate_id)

    conflicts: list[str] = []
    incompatible: set[str] = set()
    for group, ids in groups.items():
        if len(ids) > 1:
            conflicts.append(f"CONFLICT:{group} -> {','.join(ids)}")
            incompatible.update(ids)

    compatible = [c for c in passing if c.candidate_id not in incompatible]
    selected = compatible if compatible else [passing[0]]
    plan: list[str] = []
    for candidate in selected:
        plan.append(f"candidate:{candidate.candidate_id}")
        if candidate.implementation_ref:
            plan.append(f"implementation_ref:{candidate.implementation_ref}")

    total = sum(_candidate_score(c) for c in selected)
    return EnsembleResult(
        "READY_FOR_REVIEW" if not conflicts else "CONFLICT_REVIEW",
        [c.candidate_id for c in selected],
        [c.candidate_id for c in compatible],
        plan,
        conflicts,
        round(total, 4),
    )
