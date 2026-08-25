from app.learning_loop.loop import LearningLoop
from app.reward.engine import RewardEngine
from app.rl.environment.world_env import WorldRLEnvironment
from app.rl.q_learning import QLearningAgent

def test_learning_loop_trains_world_environment():
    loop=LearningLoop(WorldRLEnvironment(),QLearningAgent(seed=3),RewardEngine())
    history=loop.train(episodes=10,max_steps=20)
    assert len(history)==10
    assert loop.agent.q


def test_learning_loop_can_emit_m1_experiences():
    from app.m1.integration import M1LearningStack
    stack = M1LearningStack((0, 100, 100, 3, 1, 100), replay_capacity=64)
    loop = LearningLoop(WorldRLEnvironment(), QLearningAgent(seed=5), RewardEngine(), m1_stack=stack)
    history = loop.train(episodes=3, max_steps=5)
    assert len(history) == 3
    assert len(stack.replay) > 0
