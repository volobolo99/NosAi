from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class State:
    features: Any
    timestamp: int = 0
    scenario_id: str = "default"
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class Action:
    id: str
    parameters: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class Transition:
    state: State
    action: Action
    reward: float
    next_state: State
    done: bool
    info: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class Prediction:
    next_state: Any
    reward: float
    done_probability: float
    value: float

@dataclass(frozen=True)
class Uncertainty:
    epistemic: float
    aleatoric: float
    ood: float = 0.0
    shift: float = 0.0
    confidence: float = 1.0

@dataclass(frozen=True)
class ExperienceQuality:
    total: float
    novelty: float
    uncertainty: float
    prediction_error: float
    reward_information: float
    causal_relevance: float
    corruption_penalty: float

@dataclass(frozen=True)
class ShiftResult:
    score: float
    severity: str
    shifted: bool

@dataclass(frozen=True)
class OODResult:
    score: float
    probability: float
    confidence: float
    is_ood: bool

@dataclass(frozen=True)
class CurriculumStage:
    name: str
    difficulty: float
    horizon: int
    opponent_strength: float
    uncertainty: float
    state_complexity: float
    reward_threshold: float

@dataclass(frozen=True)
class PerformanceMetrics:
    success_rate: float
    mean_reward: float
    failure_rate: float = 0.0
    ood_rate: float = 0.0

@dataclass(frozen=True)
class DatasetManifest:
    dataset_id: str
    version: str
    environment_version: str
    scenario_version: str
    agent_version: str
    generator_version: str
    seed: int
    checksum: str
    schema_version: int = 1

@dataclass(frozen=True)
class LatentState:
    vector: tuple[float, ...]
