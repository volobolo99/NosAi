"""Memory evidence layer: retrieval advises the brain without controlling execution."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from app.memory.retrieval import MemoryMatch, MemoryRetriever


@dataclass(frozen=True)
class MemoryEvidence:
    matches: Tuple[MemoryMatch, ...]
    confidence: float
    summary: str


class MemoryEvidenceProvider:
    def __init__(self, retriever: MemoryRetriever | None = None):
        self.retriever = retriever or MemoryRetriever()

    def build(self, records, *, state_fingerprint=None, goal_kind=None, action_kind=None) -> MemoryEvidence:
        matches = tuple(self.retriever.retrieve(records, state_fingerprint=state_fingerprint, goal_kind=goal_kind, action_kind=action_kind))
        if not matches:
            return MemoryEvidence((), 0.0, "no relevant episodic evidence")
        top = matches[0]
        confidence = min(1.0, max(0.0, top.score / 10.0))
        summary = "; ".join(top.reasons) if top.reasons else "ranked episodic evidence"
        return MemoryEvidence(matches, confidence, summary)
