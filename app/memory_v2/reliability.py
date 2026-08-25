from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from math import exp


@dataclass(frozen=True)
class ReliabilityAssessment:
    memory_id: str
    base_confidence: float
    decayed_confidence: float
    status: str
    age_days: float
    provenance_count: int
    verification_count: int


class MemoryReliability:
    """Deterministic reliability layer for semantic memory.

    Confidence decays with time since verification, while repeated independent
    provenance and verification counts provide bounded support. No record is
    deleted by this layer; callers decide whether stale knowledge is usable.
    """

    def __init__(self, *, half_life_days: float = 30.0, stale_threshold: float = 0.50,
                 suspect_threshold: float = 0.10):
        if half_life_days <= 0:
            raise ValueError("half_life_days must be > 0")
        if not 0 <= suspect_threshold <= stale_threshold <= 1:
            raise ValueError("thresholds must satisfy 0 <= suspect <= stale <= 1")
        self.half_life_days = float(half_life_days)
        self.stale_threshold = float(stale_threshold)
        self.suspect_threshold = float(suspect_threshold)

    def assess(self, fact, *, now: datetime | None = None) -> ReliabilityAssessment:
        now = now or datetime.now(timezone.utc)
        verified = fact.last_verified
        if verified.tzinfo is None:
            verified = verified.replace(tzinfo=timezone.utc)
        age_days = max(0.0, (now - verified).total_seconds() / 86400.0)
        decay = 0.5 ** (age_days / self.half_life_days)
        base = max(0.0, min(1.0, float(fact.confidence)))
        # Verification/provenance strengthen confidence, but never beyond 1.
        support = min(0.20, 0.04 * max(0, int(getattr(fact, "verification_count", 1)) - 1))
        provenance = tuple(dict.fromkeys(getattr(fact, "source_refs", []) or []))
        support += min(0.10, 0.02 * max(0, len(provenance) - 1))
        decayed = min(1.0, (base + support) * decay)
        status = "trusted"
        if decayed < self.suspect_threshold:
            status = "suspect"
        elif decayed < self.stale_threshold:
            status = "stale"
        return ReliabilityAssessment(
            memory_id=str(fact.id),
            base_confidence=base,
            decayed_confidence=decayed,
            status=status,
            age_days=age_days,
            provenance_count=len(provenance),
            verification_count=int(getattr(fact, "verification_count", 1)),
        )

    def usable(self, fact, *, min_confidence: float = 0.0, now: datetime | None = None) -> bool:
        if min_confidence < 0 or min_confidence > 1:
            raise ValueError("min_confidence must be in [0, 1]")
        assessment = self.assess(fact, now=now)
        return assessment.status != "suspect" and assessment.decayed_confidence >= min_confidence
