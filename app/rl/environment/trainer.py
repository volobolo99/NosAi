
from app.rl.q_learning import QLearningAgent

class WorldRLTrainer:
    def __init__(self, environment, agent=None):
        self.environment=environment
        self.agent=agent or QLearningAgent()

    def train(self, episodes=100, max_steps=100):
        rewards=[]
        for _ in range(episodes):
            state=self.environment.reset()
            total=0.0
            for _ in range(max_steps):
                actions=self.environment.actions(state)
                action=self.agent.choose(state,actions)
                if action is None: break
                next_state,reward,done=self.environment.step(state,action)
                # World states need stable serialization for tabular learning.
                self.agent.update_raw(
                    self._key(state), getattr(action,"key",action.action_id), reward,
                    self._key(next_state), done,
                    [getattr(a,"key",a.action_id) for a in actions]
                )
                state=next_state
                total+=reward
                if done: break
            rewards.append(total)
        return rewards

    def _key(self,state):
        char=tuple(sorted(state.character.items()))
        entities=tuple(sorted(
            (k,tuple(sorted(v.attributes.items())))
            for k,v in state.entities.items()
        ))
        inv=tuple(sorted(state.inventory.items()))
        return repr((state.map_id,char,entities,inv))
