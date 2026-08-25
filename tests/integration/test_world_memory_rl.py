
from app.world_model.state import WorldState,EntityState
from app.rl.environment.world_env import WorldRLEnvironment
from app.rl.environment.trainer import WorldRLTrainer

def test_world_model_can_train_rl_without_live_client():
    state=WorldState(
        character={"hp":100,"mp":50,"position":"start"},
        entities={"mob:1":EntityState("mob:1","monster",{"hp":50})},
        inventory={"potion":2},map_id="sandbox"
    )
    env=WorldRLEnvironment(state)
    trainer=WorldRLTrainer(env)
    rewards=trainer.train(episodes=5,max_steps=10)
    assert rewards
    assert len(trainer.agent.q)>0
