
from app.rl.environment.world_env import WorldRLEnvironment
from app.rl.environment.trainer import WorldRLTrainer

def test_world_rl_training():
    env=WorldRLEnvironment()
    trainer=WorldRLTrainer(env)
    rewards=trainer.train(episodes=10,max_steps=20)
    assert len(rewards)==10
    assert trainer.agent.q
