from app.learning_loop.loop import LearningLoop
from app.world_model.state import WorldState
from app.world_model.actions import WorldAction

class Env:
    def reset(self): return WorldState(character={"hp":100})
    def actions(self,s): return [WorldAction("a","move",{"d":1})]
    def step(self,s,a): return s, 0.0, True

class Agent:
    def choose(self,s,a): return a[0]
    def update_raw(self,*args): pass

def test_learning_loop_accepts_m3_slot():
    loop=LearningLoop(Env(),Agent(),m3_stack=None)
    assert loop.train(episodes=1,max_steps=1)==[0.0]
