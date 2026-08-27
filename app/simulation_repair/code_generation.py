"""Safe interface for generated code candidates.

This module defines the boundary between researched evidence and executable
patches. Implementations may call an approved code-generation service, but the
returned text is only a candidate and must never be applied or executed here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence

from .candidate_generator import CandidateProposal


@dataclass(frozen=True)
class CodeCandidate:
    candidate_id: str
    source_candidate_id: str
    file_path: str | None
    patch_text: str
    rationale: str
    evidence_urls: tuple[str, ...]


class CodeGenerationProvider(Protocol):
    def generate(self, *, error_type: str, message: str, proposals: Sequence[CandidateProposal]) -> Sequence[CodeCandidate]:
        """Return candidate patches; implementations must not apply them."""


def validate_candidate(candidate: CodeCandidate) -> list[str]:
    """Cheap structural checks before a candidate can enter a sandbox."""
    errors: list[str] = []
    if not candidate.patch_text.strip():
        errors.append("empty patch")
    if "<script" in candidate.patch_text.lower():
        errors.append("unexpected HTML/script content in code candidate")
    if candidate.file_path and candidate.file_path.startswith(("/", "\\")):
        errors.append("absolute file path is not allowed")
    if ".." in (candidate.file_path or "").replace("\\", "/").split("/"):
        errors.append("path traversal is not allowed")
    return errors
