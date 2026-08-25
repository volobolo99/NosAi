
from dataclasses import dataclass, field

@dataclass(frozen=True)
class WorldAction:
    action_id: str
    kind: str
    parameters: dict = field(default_factory=dict)
