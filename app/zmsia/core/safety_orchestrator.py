from __future__ import annotations

from dataclasses import dataclass

from .contracts import Observation
from .orchestrator import CycleResult, ZMSIAOrchestrator
from .safety import SafetyPolicy
from .validation import validate_action


@dataclass(frozen=True)
class SafeCycleResult:
    """Result of one cycle after validation and safety policy evaluation."""

    cycle: CycleResult
    allowed: bool
    reason: str


class SafeZMSIAOrchestrator(ZMSIAOrchestrator):
    """Orchestrator variant that validates and gates every proposed action."""

    def __init__(self, decision_provider, safety_policy: SafetyPolicy) -> None:
        """Create a safe orchestrator with a concrete safety policy."""
        super().__init__(decision_provider)
        self._safety_policy = safety_policy

    def run_safe_once(self, observation: Observation) -> SafeCycleResult:
        """Run one cycle and stop before execution when validation or safety fails."""
        cycle = self.run_once(observation)
        validation = validate_action(cycle.action)
        if not validation.valid:
            return SafeCycleResult(
                cycle=cycle,
                allowed=False,
                reason="; ".join(validation.errors),
            )

        safety = self._safety_policy.validate(cycle.action)
        return SafeCycleResult(
            cycle=cycle,
            allowed=safety.allowed,
            reason=safety.reason,
        )
