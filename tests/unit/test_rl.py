
from app.rl.q_learning import QLearningAgent
from app.rl.trainer import SandboxRLTrainer
from app.rl.simple_env import SimpleGoalEnv

def test_rl_training_runs():
    agent=QLearningAgent(epsilon=.1,seed=1)
    history=SandboxRLTrainer(agent,SimpleGoalEnv()).train(episodes=50)
    assert len(history)==50
    assert agent.q
