from dataclasses import dataclass

@dataclass(frozen=True)
class LearningStep:
    state: object
    action: object
    next_state: object
    reward: float
    done: bool

class LearningLoop:
    """Connects world environment, reward engine, simulator feedback and RL."""
    def __init__(self, environment, agent, reward_engine=None, memory_store=None, m1_stack=None, m2_stack=None, m3_stack=None):
        self.environment = environment
        self.agent = agent
        self.reward_engine = reward_engine
        self.memory_store = memory_store
        self.m1_stack = m1_stack
        self.m2_stack = m2_stack
        self.m3_stack = m3_stack

    def run_episode(self, max_steps=100):
        state = self.environment.reset()
        total = 0.0
        steps = []
        for _ in range(max_steps):
            actions = self.environment.actions(state)
            if self.m3_stack is not None:
                action, _ = self.m3_stack.choose(state, actions)
            elif self.m2_stack is not None:
                action, _ = self.m2_stack.choose(state, actions)
            else:
                action = self.agent.choose(state, actions)
            if action is None:
                break
            next_state, env_reward, done = self.environment.step(state, action)
            reward = env_reward
            if self.reward_engine is not None:
                # The environment reward remains the intrinsic signal; callers
                # can enrich it with goal/risk/time/resource context later.
                reward = self.reward_engine.calculate(
                    __import__('app.reward.engine', fromlist=['RewardContext']).RewardContext(
                        intrinsic_reward=env_reward, success=done
                    )
                )
            next_actions = self.environment.actions(next_state)
            self.agent.update_raw(state, action, reward, next_state, done, next_actions)
            steps.append(LearningStep(state, action, next_state, reward, done))
            if self.m1_stack is not None:
                self.m1_stack.observe_transition(state, action, next_state, reward, done)
            total += reward
            state = next_state
            if done:
                break
        return total, tuple(steps)

    def train(self, episodes=100, max_steps=100):
        history=[]
        for _ in range(episodes):
            total, _ = self.run_episode(max_steps)
            history.append(total)
        return history
