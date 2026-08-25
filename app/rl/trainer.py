
from app.rl.q_learning import QLearningAgent

class SandboxRLTrainer:
    def __init__(self, agent, environment):
        self.agent=agent
        self.environment=environment

    def train(self, episodes=100, max_steps=100):
        history=[]
        for _ in range(episodes):
            state=self.environment.reset()
            total=0.0
            for _ in range(max_steps):
                actions=self.environment.actions(state)
                action=self.agent.choose(state,actions)
                if action is None: break
                next_state,reward,done=self.environment.step(state,action)
                self.agent.update_raw(
                    self._key(state), action.key, reward,
                    self._key(next_state), done,
                    [a.key for a in self.environment.actions(next_state)]
                )
                state=next_state
                total+=reward
                if done: break
            history.append(total)
        return history

    def _key(self,state):
        return repr(getattr(state,"key",state))
