from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from .contracts import Action, Decision, Observation, State
from .providers import DecisionProvider


@dataclass(frozen=True)
class CycleResult:
    observation: Observation
    state: State
    decision: Decision
    action: Action


class ZMSIAOrchestrator:
    """Small provider-neutral orchestration kernel.

    The first implementation intentionally stops before execution. This keeps
    the new Core safe and makes the complete observe -> decide path testable
    without requiring the live client or external tools.
    """

    def __init__(
        self,
        decision_provider: DecisionProvider,
        state_builder: Optional[Callable[[Observation], State]] = None,
    ) -> None:
        self._decision_provider = decision_provider
        self._state_builder = state_builder or self._default_state_builder

    def run_once(self, observation: Observation) -> CycleResult:
        state = self._state_builder(observation)
        decision = self._decision_provider.decide(state)
        action = decision.action
        return CycleResult(
            observation=observation,
            state=state,
            decision=decision,
            action=action,
        )

    @staticmethod
    def _default_state_builder(observation: Observation) -> State:
        return State(
            schema_version=observation.schema_version,
            state_id=f"state:{observation.observation_id}",
            timestamp=observation.timestamp,
            values={"observation_id": observation.observation_id},
            confidence=observation.confidence,
        )
