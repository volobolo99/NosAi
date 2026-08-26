from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .contracts import Action


@dataclass(frozen=True)
class SafetyDecision:
    """Outcome returned by a pre-execution safety policy."""

    allowed: bool
    reason: str


class SafetyPolicy(Protocol):
    """Protocol implemented by concrete policies used before execution."""

    def validate(self, action: Action) -> SafetyDecision:
        """Return whether the proposed action is allowed."""
        ...


class DefaultSafetyPolicy:
    """Conservative pre-execution policy for the ZMSIA dry-run core."""

    allowed_dry_run_actions = frozenset({"noop"})

    def validate(self, action: Action) -> SafetyDecision:
        """Allow only explicitly listed action types and require an ID."""
        if not action.action_id:
            return SafetyDecision(False, "action_id is required")
        if not action.action_type:
            return SafetyDecision(False, "action_type is required")
        if action.action_type not in self.allowed_dry_run_actions:
            return SafetyDecision(False, f"action type '{action.action_type}' is not enabled")
        return SafetyDecision(True, "allowed")
