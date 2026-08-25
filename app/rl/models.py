
from dataclasses import dataclass

@dataclass(frozen=True)
class RLState:
    key: str

@dataclass(frozen=True)
class RLAction:
    key: str

@dataclass(frozen=True)
class RLTransition:
    state: RLState
    action: RLAction
    reward: float
    next_state: RLState
    done: bool
