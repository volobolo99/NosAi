
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SimState:
    values: dict[str, Any] = field(default_factory=dict)

    def get(self, key, default=None):
        return self.values.get(key, default)

    def with_updates(self, **updates):
        data = dict(self.values)
        data.update(updates)
        return SimState(data)


@dataclass(frozen=True)
class SimAction:
    action_id: str
    kind: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SimOutcome:
    success: bool
    state: SimState
    reward: float
    duration_seconds: float
    risk: float
    events: tuple[str, ...] = ()


@dataclass(frozen=True)
class SimulationResult:
    strategy_id: str
    outcomes: tuple[SimOutcome, ...]
    success_probability: float
    expected_reward: float
    expected_duration: float
    expected_risk: float
