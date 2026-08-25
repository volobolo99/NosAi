
from .models import Goal, SubGoal, GoalPlan

class HierarchicalGoalPlanner:
    """Turns high-level goals into dependency-aware subgoals."""

    TEMPLATES = {
        "EXP": ("CHECK_RESOURCES", "SELECT_AREA", "TRAVEL", "FARM", "RECOVER"),
        "ITEM": ("IDENTIFY_ITEM", "CHECK_SOURCES", "SELECT_SOURCE", "ACQUIRE"),
        "QUEST": ("READ_OBJECTIVE", "LOCATE_TARGET", "TRAVEL", "COMPLETE"),
        "PVM": ("ASSESS_TARGET", "PREPARE", "ENGAGE", "LOOT", "RECOVER"),
        "PVP": ("ASSESS_OPPONENT", "PREPARE", "ENGAGE", "ADAPT", "RECOVER"),
        "UPGRADE": ("CHECK_REQUIREMENTS", "ACQUIRE_MATERIALS", "UPGRADE", "VERIFY"),
    }

    def decompose(self, goal: Goal) -> GoalPlan:
        kinds=self.TEMPLATES.get(goal.kind, ("ANALYZE","ACT","VERIFY"))
        result=[]
        previous=None
        for i,kind in enumerate(kinds):
            sid=f"{goal.id}:sub:{i}"
            deps=(previous,) if previous else ()
            result.append(SubGoal(
                id=sid, parent_id=goal.id, kind=kind,
                description=f"{kind} for {goal.description}",
                priority=goal.priority, dependencies=deps
            ))
            previous=sid
        return GoalPlan(goal.id, tuple(result))
