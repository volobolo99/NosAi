"""Verification-gated admission for benchmark gold examples.

Git history only produces candidates. This module requires explicit test evidence
before a candidate can enter the positive benchmark partition.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bug_corpus import BugCorpusExample, build_corpus


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class VerificationEvidence:
    commit: str
    status: VerificationStatus
    test_command: str
    exit_code: int
    summary: str = ""

    @property
    def passed(self) -> bool:
        return self.status is VerificationStatus.VERIFIED and self.exit_code == 0


def admit_gold(
    candidates: Iterable[BugCorpusExample],
    evidence: Iterable[VerificationEvidence],
) -> tuple[BugCorpusExample, ...]:
    """Admit only candidates with explicit successful verification evidence."""
    passed = {item.commit for item in evidence if item.passed}
    return build_corpus(
        candidate
        for candidate in candidates
        if candidate.example_id.removeprefix("git-") in passed
    )


def partition_negatives(
    candidates: Iterable[BugCorpusExample],
    evidence: Iterable[VerificationEvidence],
) -> tuple[BugCorpusExample, ...]:
    """Keep explicitly failed attempts outside positive ground truth."""
    failed = {item.commit for item in evidence if item.status is VerificationStatus.FAILED}
    return build_corpus(
        candidate
        for candidate in candidates
        if candidate.example_id.removeprefix("git-") in failed
    )
