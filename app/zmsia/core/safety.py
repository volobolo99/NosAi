from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .contracts import Action


@dataclass(frozen=True)
class SafetyDecision:
    allowed: bool
    reason: str


class SafetyPolicy(Protocol):
    def validate(self, action: Action) -> SafetyDecision: ...


class DefaultSafetyPolicy:
    """Conservative pre-execution policy for the ZMSIA core."""

    allowed_dry_run_actions = frozenset({"noop"})

    def validate(self, action: Action) -> SafetyDecision:
        if not action.action_id:
            return SafetyDecision(False, "action_id is required")
        if action.action_id not in self.allowed_dry_run_actions:
            return SafetyDecision(False, f"action id '{action.action_id}' is not enabled")
        return SafetyDecision(True, "action allowed by dry-run policy")
