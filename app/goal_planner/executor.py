
class GoalPlanExecutor:
    """Maintains plan progress; execution is delegated to external adapters."""

    def __init__(self):
        self.completed=set()

    def next_ready(self, plan):
        for subgoal in plan.ordered_subgoals:
            if subgoal.id in self.completed:
                continue
            if all(dep in self.completed for dep in subgoal.dependencies):
                return subgoal
        return None

    def mark_completed(self, subgoal_id):
        self.completed.add(subgoal_id)
