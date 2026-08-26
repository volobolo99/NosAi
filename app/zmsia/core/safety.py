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
    """Conservative pre-execution policy for the ZMSIA core.

    The first gate is deliberately deny-by-default for unknown action types.
    It is not a client executor and cannot perform side effects.
    """

    allowed_dry_run_actions = frozenset({"noop"})

    def validate(self, action: Action) -> SafetyDecision:
        if not action.action_type:
            return SafetyDecision(False, "action_type is required")
        if action.action_type not in self.allowed_dry_run_actions:
            return SafetyDecision(False, f"action type '{action.action_type}' is not enabled")
        return SafetyDecision(True, "action allowed by dry-run policy")
