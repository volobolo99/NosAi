
from statistics import mean
from .models import StrategyExperience


class StrategyLearning:
    """Learns from strategy outcomes without changing strategy code directly."""

    def __init__(self, store):
        self.store = store

    def record(self, experience: StrategyExperience):
        self.store.add_strategy_experience(experience)

    def ranking(self, goal_type):
        rows = [
            x for x in self.store.strategy_experiences
            if x.goal_type == goal_type
        ]

        grouped = {}
        for row in rows:
            grouped.setdefault(row.strategy_id, []).append(row)

        result = []
        for strategy_id, experiences in grouped.items():
            result.append({
                "strategy_id": strategy_id,
                "attempts": len(experiences),
                "success_rate": mean(
                    1.0 if x.success else 0.0 for x in experiences
                ),
                "mean_reward": mean(x.reward for x in experiences),
                "mean_duration": mean(
                    x.duration_seconds for x in experiences
                ),
                "mean_risk": mean(x.risk for x in experiences),
            })

        return sorted(
            result,
            key=lambda x: (
                x["success_rate"],
                x["mean_reward"],
                -x["mean_duration"],
                -x["mean_risk"],
            ),
            reverse=True,
        )
