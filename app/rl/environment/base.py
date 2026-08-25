
class RLEnvironment:
    """Minimal environment contract for sandbox/replay training."""

    def reset(self):
        raise NotImplementedError

    def actions(self, state):
        raise NotImplementedError

    def step(self, state, action):
        raise NotImplementedError

    def reward(self, previous, current, events):
        return 0.0
