
from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class RolloutResult:
    success: bool
    reward: float
    duration_seconds: float
    risk: float
    final_state: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class MonteCarloResult:
    strategy_id: str
    runs: int
    success_probability: float
    mean_reward: float
    mean_duration: float
    mean_risk: float
    confidence_interval_95: tuple[float, float]
    rollouts: tuple[RolloutResult, ...] = ()
