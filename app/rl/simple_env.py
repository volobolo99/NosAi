
from .models import RLState, RLAction

class SimpleGoalEnv:
    """Minimal deterministic sandbox used to validate the RL loop."""

    def reset(self):
        return RLState("start")

    def actions(self,state):
        if state.key=="start":
            return [RLAction("safe"),RLAction("fast")]
        if state.key=="mid":
            return [RLAction("finish")]
        return []

    def step(self,state,action):
        if state.key=="start" and action.key=="safe":
            return RLState("mid"),1.0,False
        if state.key=="start" and action.key=="fast":
            return RLState("done"),0.5,True
        if state.key=="mid" and action.key=="finish":
            return RLState("done"),3.0,True
        return RLState("done"),-1.0,True
