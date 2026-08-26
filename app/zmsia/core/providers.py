"""Provider interfaces for ZMSIA reasoning.

The Core depends on this protocol, never on an SDK-specific implementation.
A real OpenAI adapter can implement the same interface later; tests use the
mock provider and remain deterministic/offline.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .contracts import Decision, Plan, State


class DecisionProvider(Protocol):
    """Minimum contract required by the ZMSIA orchestrator."""

    name: str

    def decide(self, *, state: State, plan: Plan) -> Decision:
        """Return a provider-neutral decision for the current state/plan."""
        ...


@dataclass(frozen=True)
class MockDecisionProvider:
    """Deterministic provider for unit/integration tests and dry runs."""

    name: str = "mock"
    action_id: str = "noop"

    def decide(self, *, state: State, plan: Plan) -> Decision:
        return Decision(
            decision_id=f"mock:{state.state_id}:{plan.plan_id}",
            goal_id=plan.goal_id,
            action_id=self.action_id,
            parameters={},
            rationale="Deterministic mock decision; no external side effects.",
            confidence=1.0,
            provider=self.name,
            plan_id=plan.plan_id,
        )
