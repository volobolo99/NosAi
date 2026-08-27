"""G3.9 runtime integration safety gate.

This gate validates proposed runtime operations without executing them.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .adapter import RuntimeCommand


class GateDecision(str, Enum):
    ALLOW_SANDBOX = "allow_sandbox"
    DENY = "deny"


@dataclass(frozen=True)
class SafetyPolicy:
    allowed_actions: frozenset[str]
    require_session: bool = True
    max_parameters: int = 16


@dataclass(frozen=True)
class SafetyEvaluation:
    decision: GateDecision
    reason: str


class RuntimeSafetyGate:
    """Deny-by-default policy boundary for sandbox operations."""

    def __init__(self, policy: SafetyPolicy) -> None:
        self._policy = policy

    def evaluate(self, command: RuntimeCommand, *, session_active: bool, kill_switch_engaged: bool = True) -> SafetyEvaluation:
        if kill_switch_engaged:
            return SafetyEvaluation(GateDecision.DENY, "kill switch engaged")
        if self._policy.require_session and not session_active:
            return SafetyEvaluation(GateDecision.DENY, "active session required")
        if command.action not in self._policy.allowed_actions:
            return SafetyEvaluation(GateDecision.DENY, "action not allowlisted")
        if len(command.parameters) > self._policy.max_parameters:
            return SafetyEvaluation(GateDecision.DENY, "parameter limit exceeded")
        return SafetyEvaluation(GateDecision.ALLOW_SANDBOX, "sandbox policy satisfied")
