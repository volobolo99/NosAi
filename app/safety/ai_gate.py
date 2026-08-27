"""Deterministic gate between AI planning and action execution."""
from __future__ import annotations


def validate_ai_decision(decision, *, observation_valid: bool, live_actions_enabled: bool) -> dict:
    if not observation_valid:
        return {"status": "REJECTED", "reason": "INVALID_OBSERVATION", "action": "noop"}
    if decision is None:
        return {"status": "REJECTED", "reason": "NO_DECISION", "action": "noop"}
    confidence = float(getattr(decision, "confidence", 0.0))
    if not 0.0 <= confidence <= 1.0:
        return {"status": "REJECTED", "reason": "INVALID_CONFIDENCE", "action": "noop"}
    selected = getattr(decision, "selected", None)
    if selected is None:
        return {"status": "REJECTED", "reason": "NO_ACTION_INTENT", "action": "noop"}
    if not live_actions_enabled:
        return {"status": "PROPOSAL_ONLY", "reason": "LIVE_ACTIONS_DISABLED", "action": selected.kind.value}
    return {"status": "VALIDATED", "action": selected.kind.value, "confidence": confidence}
