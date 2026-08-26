from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .contracts import Action, Decision, Observation, Plan, State
from .providers import DecisionProvider


@dataclass(frozen=True)
class CycleResult:
    """Immutable output of one provider-neutral ZMSIA planning cycle."""

    observation: Observation
    state: State
    plan: Plan
    decision: Decision
    action: Action


class ZMSIAOrchestrator:
    """Provider-neutral planning/decision kernel.

    Execution is deliberately outside this class. The kernel can therefore be
    exercised with deterministic providers before any live client integration.
    """

    def __init__(
        self,
        decision_provider: DecisionProvider,
        plan_builder: Callable[[State], Plan] | None = None,
        state_builder: Callable[[Observation], State] | None = None,
    ) -> None:
        """Create an orchestrator with optional state and plan builders."""
        self._decision_provider = decision_provider
        self._plan_builder = plan_builder or self._default_plan_builder
        self._state_builder = state_builder or self._default_state_builder

    def run_once(self, observation: Observation) -> CycleResult:
        """Run one deterministic observe-to-action cycle without executing it."""
        state = self._state_builder(observation)
        plan = self._plan_builder(state)
        decision = self._decision_provider.decide(state=state, plan=plan)
        action = Action(
            action_id=decision.action_id,
            action_type=decision.action_type,
            parameters=dict(decision.parameters),
            decision_id=decision.decision_id,
        )
        return CycleResult(observation, state, plan, decision, action)

    @staticmethod
    def _default_state_builder(observation: Observation) -> State:
        """Build a normalized state directly from one observation."""
        return State(
            state_id=f"state:{observation.observation_id}",
            timestamp_ms=observation.timestamp_ms,
            values=dict(observation.data),
            confidence=observation.confidence,
            source_observation_ids=(observation.observation_id,),
        )

    @staticmethod
    def _default_plan_builder(state: State) -> Plan:
        """Build the deterministic no-op baseline plan used by dry-run tests."""
        return Plan(
            plan_id=f"plan:{state.state_id}",
            goal_id="default",
            steps=("noop",),
            rationale="Deterministic baseline plan.",
            confidence=1.0,
            provider="core-default",
        )
