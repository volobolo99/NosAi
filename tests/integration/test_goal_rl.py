
from app.goal_planner.models import Goal
from app.goal_planner.hierarchical import HierarchicalGoalPlanner
from app.rl.q_learning import QLearningAgent
from app.rl.trainer import SandboxRLTrainer
from app.rl.simple_env import SimpleGoalEnv

def test_goal_and_rl_components_coexist():
    plan=HierarchicalGoalPlanner().decompose(
        Goal("g","EXP","gain experience")
    )
    agent=QLearningAgent(seed=2)
    history=SandboxRLTrainer(agent,SimpleGoalEnv()).train(20)
    assert plan.goal_id=="g"
    assert history
