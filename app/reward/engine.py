from dataclasses import dataclass, field

@dataclass(frozen=True)
class RewardWeights:
    goal_progress: float = 10.0
    success: float = 25.0
    reward: float = 1.0
    time_penalty: float = 0.15
    risk_penalty: float = 5.0
    resource_penalty: float = 1.0
    failure_penalty: float = 30.0

@dataclass(frozen=True)
class RewardContext:
    goal_progress: float = 0.0
    success: bool = False
    intrinsic_reward: float = 0.0
    duration_seconds: float = 0.0
    risk: float = 0.0
    resources_used: float = 0.0
    failed: bool = False
    metadata: dict = field(default_factory=dict)

class RewardEngine:
    """Combines goal, efficiency, risk and outcome signals into one RL reward."""
    def __init__(self, weights=None):
        self.weights = weights or RewardWeights()

    def calculate(self, c: RewardContext) -> float:
        w = self.weights
        value = (
            w.goal_progress * c.goal_progress
            + w.success * float(c.success)
            + w.reward * c.intrinsic_reward
            - w.time_penalty * c.duration_seconds
            - w.risk_penalty * c.risk
            - w.resource_penalty * c.resources_used
        )
        if c.failed:
            value -= w.failure_penalty
        return value
