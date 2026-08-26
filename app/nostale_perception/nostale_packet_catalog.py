"""Versioned NosTale packet catalog with provenance and confidence.

Entries are references/hypotheses until validated against replay fixtures. The
catalog contains no traffic interception or packet injection logic.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class PacketDefinition:
    header: str
    direction: str
    kind: str
    schema_version: str
    confidence: float
    provenance: str
    notes: str = ""

    def __post_init__(self) -> None:
        if self.direction not in {"send", "recv", "unknown"}:
            raise ValueError("direction must be send, recv, or unknown")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


class PacketCatalog:
    def __init__(self, version: str) -> None:
        self.version = version
        self._entries: dict[tuple[str, str], PacketDefinition] = {}

    def add(self, definition: PacketDefinition) -> None:
        key = (definition.direction, definition.header)
        if key in self._entries:
            raise ValueError(f"duplicate packet definition: {key}")
        self._entries[key] = definition

    def get(self, direction: str, header: str) -> PacketDefinition | None:
        return self._entries.get((direction, header)) or self._entries.get(("unknown", header))

    def entries(self) -> tuple[PacketDefinition, ...]:
        return tuple(sorted(self._entries.values(), key=lambda x: (x.header, x.direction)))

    def to_json(self, path: str | Path) -> None:
        payload = {"version": self.version, "packets": [asdict(e) for e in self.entries()]}
        Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    @classmethod
    def from_json(cls, path: str | Path) -> "PacketCatalog":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        catalog = cls(payload["version"])
        for item in payload["packets"]:
            catalog.add(PacketDefinition(**item))
        return catalog
