from app.learning_loop.loop import LearningLoop
from app.m1.integration import M1LearningStack
from app.m2.integration import M2PlanningStack
from app.rl.environment.world_env import WorldRLEnvironment

# Smoke integration only: planner can be injected without altering the legacy path.
def test_m2_stack_constructs_and_plans():
    m1=M1LearningStack(reference_features=(0,100,100,3,1,100), seed=3)
    m2=M2PlanningStack(m1, simulations=8, horizon=2, seed=3)
    env=WorldRLEnvironment()
    state=env.reset()
    actions=env.actions(state)
    action,result=m2.choose(state,actions)
    assert action is not None
    assert result.actions
