from __future__ import annotations
from collections.abc import Sequence
from app.m1.core.types import Action, State
from .types import ImaginedStep, ImaginedTrajectory

class ImaginationEngine:
    """Generate future trajectories entirely inside the learned World Model."""
    def __init__(self, world_model, discount: float = 0.99):
        if not 0.0 < discount <= 1.0:
            raise ValueError("discount must be in (0, 1]")
        self.world_model = world_model
        self.discount = discount

    def imagine(self, state: State, action_sequences: Sequence[Sequence[Action]]) -> tuple[ImaginedTrajectory, ...]:
        return tuple(self.rollout(state, actions) for actions in action_sequences)

    def rollout(self, state: State, actions: Sequence[Action]) -> ImaginedTrajectory:
        current = state
        steps = []
        total = 0.0
        discounted = 0.0
        terminal_probability = 0.0
        uncertainty_sum = 0.0
        discount = 1.0
        for action in actions:
            prediction = self.world_model.predict(current, action)
            unc = self._uncertainty(current, action)
            total += prediction.reward
            discounted += discount * prediction.reward
            terminal_probability = 1.0 - (1.0 - terminal_probability) * (1.0 - prediction.done_probability)
            uncertainty_sum += discount * unc
            steps.append(ImaginedStep(current, action, prediction, total, discounted, unc))
            current = prediction.next_state
            discount *= self.discount
            if prediction.done_probability >= 0.999:
                break
        return ImaginedTrajectory(tuple(steps), total, discounted, terminal_probability, uncertainty_sum)

    def _uncertainty(self, state, action) -> float:
        try:
            u = self.world_model.uncertainty(state, action)
            return max(0.0, float(u.epistemic + u.aleatoric + u.ood + u.shift))
        except (AttributeError, TypeError):
            return 0.0
