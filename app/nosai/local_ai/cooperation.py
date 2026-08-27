"""Cooperation policy between the primary AI and the local secondary AI.

This module defines the decision protocol only. Concrete model/runtime selection,
training and game-specific policies are intentionally deferred to later gates.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class CooperationMode(str, Enum):
    PRIMARY_ONLY = "primary_only"
    LOCAL_ASSIST = "local_assist"
    DUAL_REVIEW = "dual_review"
    LOCAL_FALLBACK = "local_fallback"


class DecisionRole(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    CONSENSUS = "consensus"


@dataclass(frozen=True)
class CooperationRequest:
    task: str
    context: Mapping[str, Any]
    urgency_ms: int | None = None
    risk_level: float = 0.0
    require_local: bool = False


@dataclass(frozen=True)
class AIProposal:
    source: DecisionRole
    action: str
    confidence: float
    rationale: str = ""
    metadata: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class CooperationDecision:
    mode: CooperationMode
    selected: DecisionRole
    action: str
    confidence: float
    proposals: tuple[AIProposal, ...] = ()
    reason: str = ""


class CooperationPolicy:
    """Deterministic arbitration layer; it never executes game actions itself."""

    def choose_mode(self, request: CooperationRequest, local_ready: bool) -> CooperationMode:
        if request.require_local and local_ready:
            return CooperationMode.LOCAL_ASSIST
        if not local_ready:
            return CooperationMode.PRIMARY_ONLY
        if request.risk_level >= 0.75:
            return CooperationMode.DUAL_REVIEW
        if request.urgency_ms is not None and request.urgency_ms <= 150:
            return CooperationMode.PRIMARY_ONLY
        return CooperationMode.LOCAL_ASSIST

    def arbitrate(
        self,
        request: CooperationRequest,
        primary: AIProposal,
        secondary: AIProposal | None,
        local_ready: bool,
    ) -> CooperationDecision:
        mode = self.choose_mode(request, local_ready)

        if mode is CooperationMode.PRIMARY_ONLY or secondary is None:
            return CooperationDecision(
                mode=mode,
                selected=DecisionRole.PRIMARY,
                action=primary.action,
                confidence=primary.confidence,
                proposals=(primary,),
                reason="Primary path selected by availability/latency policy.",
            )

        if mode is CooperationMode.LOCAL_ASSIST:
            # Secondary advises; primary remains authoritative.
            return CooperationDecision(
                mode=mode,
                selected=DecisionRole.PRIMARY,
                action=primary.action,
                confidence=min(1.0, (primary.confidence * 0.7) + (secondary.confidence * 0.3)),
                proposals=(primary, secondary),
                reason="Local AI contributes auxiliary evidence; primary remains authoritative.",
            )

        if primary.action == secondary.action:
            return CooperationDecision(
                mode=mode,
                selected=DecisionRole.CONSENSUS,
                action=primary.action,
                confidence=max(primary.confidence, secondary.confidence),
                proposals=(primary, secondary),
                reason="High-risk task received matching proposals from both AIs.",
            )

        # Disagreement: fail closed to the primary proposal until a future
        # confidence/safety adjudicator is implemented.
        return CooperationDecision(
            mode=mode,
            selected=DecisionRole.PRIMARY,
            action=primary.action,
            confidence=primary.confidence * 0.8,
            proposals=(primary, secondary),
            reason="Dual review disagreement; primary selected conservatively and execution should be gated.",
        )


__all__ = [
    "AIProposal",
    "CooperationDecision",
    "CooperationMode",
    "CooperationPolicy",
    "CooperationRequest",
    "DecisionRole",
]
