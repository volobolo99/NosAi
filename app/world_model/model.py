
from .state import WorldState
from .actions import WorldAction

class WorldModel:
    """Pure state-transition model for simulation/replay."""

    def apply(self, state: WorldState, action: WorldAction, rng=None):
        raise NotImplementedError

    def observe(self, state: WorldState):
        return state
