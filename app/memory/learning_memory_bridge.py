"""Observational bridge from LearningLoop transitions into episodic memory.

The bridge records experiences without changing action selection or execution.
"""
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
    """Translate generic learning transitions into bounded episodic records."""

    def __init__(self, memory, source: str = "learning_loop"):
        self.memory = memory
        self.source = source

    def record_transition(self, state, action, next_state, reward: float, done: bool) -> MemoryRecord:
        kind = action if isinstance(action, ActionKind) else ActionKind(str(action)) if str(action) in {k.value for k in ActionKind} else ActionKind.NOOP
        intent = ActionIntent(kind=kind, parameters={"raw_action": action}, source=self.source)
        goal = Goal(kind="episode_complete" if done else "progress", provenance=self.source)
        outcome = Outcome(status="success" if done else "ongoing", state_delta={"next_state": next_state})
        evidence = RewardEvidence(components={"total": float(reward)}, source=self.source)
        record = MemoryRecord(_fingerprint(state), goal, intent, outcome, evidence, provenance=self.source)
        self.memory.add(record)
        return record
