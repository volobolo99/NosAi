from app.goal_planner.models import Goal
from app.m1.core.types import Action, Prediction, State
from app.m2.objective import PlannerObjective


def test_goal_progress_increases_towards_target():
    goal = Goal("g", "ITEM", "reach target", constraints={
        "target_features": {0: 10.0},
        "feature_tolerances": {0: 0.0},
    })
    obj = PlannerObjective(progress_weight=2.0)
    before = obj.goal_progress(State((2.0,)), goal)
    after = obj.goal_progress(State((8.0,)), goal)
    assert after > before


def test_goal_aware_utility_prefers_progress_when_reward_matches():
    goal = Goal("g", "ITEM", "reach target", constraints={
        "target_features": {0: 10.0},
    })
    obj = PlannerObjective(reward_weight=1.0, progress_weight=5.0,
                           risk_weight=0.0, uncertainty_weight=0.0)
    state = State((0.0,))
    safe_progress = Prediction(State((8.0,)), 1.0, 0.0, 1.0)
    no_progress = Prediction(State((0.0,)), 1.0, 0.0, 1.0)
    safe_action = Action("advance", {})
    assert obj.trajectory_step_utility(state, safe_action, safe_progress, 0.0, goal=goal) > \
           obj.trajectory_step_utility(state, safe_action, no_progress, 0.0, goal=goal)


def test_goal_completion_adds_completion_value():
    goal = Goal("g", "ITEM", "reach target", constraints={
        "target_features": {0: 10.0},
        "feature_tolerances": {0: 0.1},
    })
    obj = PlannerObjective(reward_weight=0.0, progress_weight=0.0,
                           completion_weight=3.0, risk_weight=0.0,
                           uncertainty_weight=0.0)
    state = State((9.0,))
    prediction = Prediction(State((10.0,)), 0.0, 0.0, 0.0)
    assert obj.trajectory_step_utility(state, Action("a", {}), prediction, 0.0, goal=goal) >= 3.0
