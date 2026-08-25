from random import Random
from ..core.types import Transition
class OpponentPool:
    def __init__(self, seed=0): self.agents=[]; self.rng=Random(seed)
    def register(self, agent): self.agents.append(agent)
    def sample(self):
        if not self.agents: raise ValueError("opponent pool is empty")
        return self.rng.choice(self.agents)
class SelfPlayManager:
    def __init__(self, pool, seed=0): self.pool=pool; self.rng=Random(seed)
    def generate_episode(self, agent, opponent, scenario, max_steps=None):
        if not hasattr(agent,'act') or not hasattr(opponent,'act'): raise TypeError('agents need act()')
        state = agent.reset(scenario) if hasattr(agent,'reset') else scenario
        transitions=[]; limit=max_steps or int(scenario.get('horizon',10))
        for t in range(limit):
            action=agent.act(state); next_state=agent.step(state, action, opponent) if hasattr(agent,'step') else state
            reward=agent.reward(state, action, next_state) if hasattr(agent,'reward') else 0.0
            done=(t==limit-1)
            transitions.append(Transition(state,action,float(reward),next_state,done,{'opponent':getattr(opponent,'id','unknown')}))
            state=next_state
            if done: break
        return transitions
