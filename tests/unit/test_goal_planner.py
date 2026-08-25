
from app.goal_planner.models import Goal
from app.goal_planner.hierarchical import HierarchicalGoalPlanner
from app.goal_planner.executor import GoalPlanExecutor

def test_goal_decomposition():
    plan=HierarchicalGoalPlanner().decompose(
        Goal("g","QUEST","finish quest")
    )
    assert plan.ordered_subgoals[0].kind=="READ_OBJECTIVE"
    assert plan.ordered_subgoals[-1].kind=="COMPLETE"

def test_dependencies_gate_progress():
    plan=HierarchicalGoalPlanner().decompose(
        Goal("g","ITEM","get item")
    )
    ex=GoalPlanExecutor()
    first=ex.next_ready(plan)
    assert first.id==plan.ordered_subgoals[0].id
    ex.mark_completed(first.id)
    assert ex.next_ready(plan).id==plan.ordered_subgoals[1].id
