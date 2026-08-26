from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from .contracts import Action, Decision, Observation, Plan, State
from .providers import DecisionProvider


@dataclass(frozen=True)
class CycleResult:
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
        plan_builder: Optional[Callable[[State], Plan]] = None,
        state_builder: Optional[Callable[[Observation], State]] = None,
    ) -> None:
        self._decision_provider = decision_provider
        self._plan_builder = plan_builder or self._default_plan_builder
        self._state_builder = state_builder or self._default_state_builder

    def run_once(self, observation: Observation) -> CycleResult:
        state = self._state_builder(observation)
        plan = self._plan_builder(state)
        decision = self._decision_provider.decide(state=state, plan=plan)
        action = Action(
            action_id=decision.action_id,
            parameters=dict(decision.parameters),
            decision_id=decision.decision_id,
        )
        return CycleResult(observation, state, plan, decision, action)

    @staticmethod
    def _default_state_builder(observation: Observation) -> State:
        return State(
            state_id=f"state:{observation.observation_id}",
            timestamp_ms=observation.timestamp_ms,
            values=dict(observation.data),
            confidence=observation.confidence,
            source_observation_ids=(observation.observation_id,),
        )

    @staticmethod
    def _default_plan_builder(state: State) -> Plan:
        return Plan(
            plan_id=f"plan:{state.state_id}",
            goal_id="default",
            steps=("noop",),
            rationale="Deterministic baseline plan.",
            confidence=1.0,
            provider="core-default",
        )
