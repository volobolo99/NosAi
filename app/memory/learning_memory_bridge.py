"""Observational bridge from LearningLoop transitions into episodic memory."""
from __future__ import annotations

import hashlib
import json
from typing import Any

from app.ai.contracts import ActionIntent, ActionKind, Goal, MemoryRecord, Outcome, RewardEvidence


def _fingerprint(state: Any) -> str:
    try:
        payload = json.dumps(state, sort_keys=True, default=str, separators=(",", ":"))
    except TypeError:
        payload = repr(state)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


class LearningMemoryBridge:
    """Translate learning transitions into bounded episodic records, read-only to control."""

    def __init__(self, memory, source: str = "learning_loop"):
        self.memory = memory
        self.source = source

    def record_transition(self, state, action, next_state, reward: float, done: bool) -> MemoryRecord:
        raw = action.value if isinstance(action, ActionKind) else str(action)
        try:
            kind = ActionKind(raw)
        except ValueError:
            kind = ActionKind.NOOP
        intent = ActionIntent(kind=kind, parameters={"raw_action": action}, source=self.source)
        goal = Goal(kind="episode_complete" if done else "progress", provenance=self.source)
        outcome = Outcome(status="success" if done else "ongoing", state_delta={"next_state": next_state})
        evidence = RewardEvidence(components={"total": float(reward)}, source=self.source)
        record = MemoryRecord(_fingerprint(state), goal, intent, outcome, evidence, provenance=self.source)
        self.memory.append(record)
        return record
