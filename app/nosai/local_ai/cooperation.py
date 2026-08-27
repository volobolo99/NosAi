"""Primary/secondary AI cooperation, shared context and consensus arbitration."""

from dataclasses import dataclass, field
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
class SharedContext:
    """Read-only context snapshot sent to both AIs."""
    state_id: str
    task: str
    facts: Mapping[str, Any]
    constraints: Mapping[str, Any] = field(default_factory=dict)
    memory_refs: tuple[str, ...] = ()
    schema_version: str = "1.0"


@dataclass(frozen=True)
class CooperationRequest:
    task: str
    context: Mapping[str, Any]
    urgency_ms: int | None = None
    risk_level: float = 0.0
    require_local: bool = False
    context_snapshot: SharedContext | None = None


@dataclass(frozen=True)
class AIProposal:
    source: DecisionRole
    action: str
    confidence: float
    rationale: str = ""
    evidence: tuple[str, ...] = ()
    metadata: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class ConsensusResult:
    agreement: bool
    score: float
    reason: str


@dataclass(frozen=True)
class CooperationDecision:
    mode: CooperationMode
    selected: DecisionRole
    action: str
    confidence: float
    proposals: tuple[AIProposal, ...] = ()
    consensus: ConsensusResult | None = None
    reason: str = ""


class CooperationPolicy:
    """Deterministic arbitration layer; never executes game actions itself."""

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

    def build_context(self, request: CooperationRequest) -> SharedContext:
        if request.context_snapshot is not None:
            return request.context_snapshot
        return SharedContext(state_id="ephemeral", task=request.task, facts=dict(request.context))

    @staticmethod
    def compare(primary: AIProposal, secondary: AIProposal) -> ConsensusResult:
        same_action = primary.action == secondary.action
        confidence_gap = abs(primary.confidence - secondary.confidence)
        score = (0.7 if same_action else 0.0) + (0.3 * max(0.0, 1.0 - confidence_gap))
        return ConsensusResult(
            agreement=same_action,
            score=round(score, 4),
            reason="Matching actions." if same_action else "Conflicting actions require safety adjudication.",
        )

    def arbitrate(self, request: CooperationRequest, primary: AIProposal,
                  secondary: AIProposal | None, local_ready: bool) -> CooperationDecision:
        mode = self.choose_mode(request, local_ready)
        if mode is CooperationMode.PRIMARY_ONLY or secondary is None:
            return CooperationDecision(mode, DecisionRole.PRIMARY, primary.action, primary.confidence,
                                       (primary,), reason="Primary path selected by availability/latency policy.")

        consensus = self.compare(primary, secondary)
        if mode is CooperationMode.LOCAL_ASSIST:
            return CooperationDecision(
                mode, DecisionRole.PRIMARY, primary.action,
                min(1.0, primary.confidence * 0.7 + secondary.confidence * 0.3),
                (primary, secondary), consensus,
                "Secondary provides evidence; primary remains authoritative.",
            )

        if consensus.agreement:
            return CooperationDecision(
                mode, DecisionRole.CONSENSUS, primary.action, consensus.score,
                (primary, secondary), consensus,
                "High-risk task passed dual review with matching proposals.",
            )

        return CooperationDecision(
            mode, DecisionRole.PRIMARY, primary.action, primary.confidence * 0.8,
            (primary, secondary), consensus,
            "Disagreement: fail closed and require the safety gate before execution.",
        )


__all__ = ["AIProposal", "ConsensusResult", "CooperationDecision", "CooperationMode",
           "CooperationPolicy", "CooperationRequest", "DecisionRole", "SharedContext"]
