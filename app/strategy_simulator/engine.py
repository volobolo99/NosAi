
from dataclasses import dataclass
from .models import SimState, SimAction, SimOutcome, SimulationResult


class TransitionModel:
    """Deterministic transition model for replay/sandbox simulations."""

    def apply(self, state: SimState, action: SimAction) -> SimOutcome:
        raise NotImplementedError


class StrategySimulator:
    def __init__(self, transition_model: TransitionModel):
        self.transition_model = transition_model

    def run(self, strategy_id, initial_state, actions, runs=1):
        outcomes = []

        for _ in range(max(1, runs)):
            state = initial_state
            events = []
            total_reward = 0.0
            total_duration = 0.0
            total_risk = 0.0
            success = True

            for action in actions:
                outcome = self.transition_model.apply(state, action)
                state = outcome.state
                events.extend(outcome.events)
                total_reward += outcome.reward
                total_duration += outcome.duration_seconds
                total_risk += outcome.risk

                if not outcome.success:
                    success = False
                    break

            outcomes.append(SimOutcome(
                success=success,
                state=state,
                reward=total_reward,
                duration_seconds=total_duration,
                risk=total_risk,
                events=tuple(events),
            ))

        n = len(outcomes)
        return SimulationResult(
            strategy_id=strategy_id,
            outcomes=tuple(outcomes),
            success_probability=sum(x.success for x in outcomes) / n,
            expected_reward=sum(x.reward for x in outcomes) / n,
            expected_duration=sum(x.duration_seconds for x in outcomes) / n,
            expected_risk=sum(x.risk for x in outcomes) / n,
        )
