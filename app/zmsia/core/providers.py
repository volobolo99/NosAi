"""Provider interfaces for ZMSIA reasoning."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .contracts import Decision, Plan, State


class DecisionProvider(Protocol):
    """Minimum contract required by the ZMSIA orchestrator."""

    name: str

    def decide(self, *, state: State, plan: Plan) -> Decision:
        """Return a provider-neutral decision for the current state and plan."""
        ...


@dataclass(frozen=True)
class MockDecisionProvider:
    """Deterministic provider for unit/integration tests and dry runs."""

    name: str = "mock"
    action_type: str = "noop"

    def decide(self, *, state: State, plan: Plan) -> Decision:
        """Produce a deterministic action without external side effects."""
        return Decision(
            decision_id=f"mock:{state.state_id}:{plan.plan_id}",
            goal_id=plan.goal_id,
            action_id=f"mock-action:{state.state_id}:{plan.plan_id}",
            action_type=self.action_type,
            parameters={},
            rationale="Deterministic mock decision; no external side effects.",
            confidence=1.0,
            provider=self.name,
            plan_id=plan.plan_id,
        )
