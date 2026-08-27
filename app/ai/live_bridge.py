from __future__ import annotations

from typing import Any

from .brain import BrainObservation, NosAiBrain

REQUIRED_LIVE_FEATURES = ("hp_ratio", "mp_ratio", "target_distance", "target_resistance")


def decide_from_live_world(world: dict[str, Any], brain: NosAiBrain | None = None) -> dict[str, Any]:
    """Evaluate a real observation only when normalized Brain features exist."""
    values = world.get("brain_features") if isinstance(world.get("brain_features"), dict) else {}
    missing = [key for key in REQUIRED_LIVE_FEATURES if not isinstance(values.get(key), (int, float))]
    if missing:
        return {"status": "NOT_RUN", "reason": "live observation lacks normalized Brain features", "missing_features": missing, "observation_only": True}
    observation = BrainObservation(values={key: float(value) for key, value in values.items() if isinstance(value, (int, float))})
    decision = (brain or NosAiBrain()).decide(observation)
    return {
        "status": "READY", "action": decision.action_type, "confidence": decision.confidence,
        "reasons": list(decision.reasons), "safe_fallback": decision.safe_fallback, "observation_only": True,
        "candidates": [{"action": item.action_type, "score": item.score, "risk": item.risk, "urgency": item.urgency, "reason": item.reason} for item in decision.candidates],
    }
