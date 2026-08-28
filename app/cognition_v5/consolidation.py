"""Controlled replay/consolidation pipeline for episodic learning."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .memory import Episode, KnowledgeRecord


@dataclass(frozen=True, slots=True)
class ConsolidationCandidate:
    kind: str
    content: str
    confidence: float
    evidence_count: int
    source: str = "episodic-replay"


class ConsolidationPipeline:
    """Turns repeated experience into reviewable knowledge candidates.

    Promotion is intentionally separate from extraction. A candidate is not
    long-term knowledge until an external validator approves it.
    """

    def extract(self, episodes: Iterable[Episode]) -> tuple[ConsolidationCandidate, ...]:
        grouped: dict[str, list[Episode]] = {}
        for episode in episodes:
            grouped.setdefault(episode.action_id, []).append(episode)

        candidates: list[ConsolidationCandidate] = []
        for action_id, rows in grouped.items():
            successes = sum(row.outcome == "success" for row in rows)
            confidence = successes / len(rows)
            mean_reward = sum(row.reward for row in rows) / len(rows)
            candidates.append(
                ConsolidationCandidate(
                    kind="strategy_evidence",
                    content=f"{action_id}: mean_reward={mean_reward:.6f}; success_rate={confidence:.6f}",
                    confidence=confidence,
                    evidence_count=len(rows),
                )
            )
        return tuple(candidates)

    def promote(self, candidate: ConsolidationCandidate, *, minimum_confidence: float = 0.8) -> KnowledgeRecord | None:
        if candidate.evidence_count < 3 or candidate.confidence < minimum_confidence:
            return None
        return KnowledgeRecord(
            record_id=f"consolidated:{candidate.kind}:{candidate.evidence_count}",
            kind=candidate.kind,
            content=candidate.content,
            confidence=candidate.confidence,
            source=candidate.source,
            evidence_count=candidate.evidence_count,
        )
