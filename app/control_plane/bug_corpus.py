"""Build a deterministic, secret-safe retrieval corpus from repository evidence.

The corpus is intentionally based on already materialized repository text and
metadata. It never executes project code and applies conservative redaction
before examples become embedding input.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, Mapping

_SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|token|password|secret)\s*[:=]\s*['\"]?[^\s'\"]+"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]+"),
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
)


@dataclass(frozen=True, slots=True)
class BugCorpusExample:
    example_id: str
    repository_id: str
    project_id: str
    query: str
    relevant_documents: tuple[str, ...]
    metadata: Mapping[str, str]


def sanitize(text: str) -> str:
    """Redact common credential-like values before indexing."""
    value = text
    for pattern in _SECRET_PATTERNS:
        value = pattern.sub("[REDACTED]", value)
    return value


def build_bug_example(
    *,
    example_id: str,
    repository_id: str,
    project_id: str,
    error_signature: str,
    stack_trace: str = "",
    affected_files: Iterable[str] = (),
    failed_tests: Iterable[str] = (),
    root_cause: str = "",
    patch_summary: str = "",
    lesson: str = "",
) -> BugCorpusExample:
    """Create one retrieval example while keeping query and ground truth distinct."""
    query_parts = [error_signature, stack_trace, " ".join(affected_files), " ".join(failed_tests)]
    query = sanitize("\n".join(part for part in query_parts if part))
    relevant = tuple(
        sanitize(item)
        for item in (root_cause, patch_summary, lesson)
        if item
    )
    return BugCorpusExample(
        example_id=example_id,
        repository_id=repository_id,
        project_id=project_id,
        query=query,
        relevant_documents=relevant,
        metadata={"domain": "code-bug", "language": "mixed"},
    )


def build_corpus(records: Iterable[BugCorpusExample]) -> tuple[BugCorpusExample, ...]:
    """Return stable, de-duplicated corpus ordering."""
    unique: dict[str, BugCorpusExample] = {}
    for record in records:
        unique.setdefault(record.example_id, record)
    return tuple(unique[key] for key in sorted(unique))
