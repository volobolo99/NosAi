
from dataclasses import dataclass, field
from typing import Any

@dataclass
class EntityState:
    entity_id: str
    entity_type: str
    attributes: dict[str, Any] = field(default_factory=dict)

@dataclass
class WorldState:
    tick: int = 0
    character: dict[str, Any] = field(default_factory=dict)
    entities: dict[str, EntityState] = field(default_factory=dict)
    map_id: str | None = None
    inventory: dict[str, int] = field(default_factory=dict)
    quests: dict[str, str] = field(default_factory=dict)
    flags: dict[str, Any] = field(default_factory=dict)

    def copy(self):
        return WorldState(
            tick=self.tick,
            character=dict(self.character),
            entities=dict(self.entities),
            map_id=self.map_id,
            inventory=dict(self.inventory),
            quests=dict(self.quests),
            flags=dict(self.flags),
        )
