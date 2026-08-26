"""Versioned NosTale packet catalog independent from transport and decoders."""
from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path


@dataclass(frozen=True)
class PacketSpec:
    header: str
    direction: str
    kind: str
    schema_version: str
    confidence: float = 0.0
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.header or self.direction not in {"send", "recv"}:
            raise ValueError("invalid packet specification")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


class PacketCatalog:
    def __init__(self, specs: list[PacketSpec] | None = None) -> None:
        self._specs: dict[tuple[str, str], PacketSpec] = {}
        for spec in specs or []:
            self.register(spec)

    def register(self, spec: PacketSpec) -> None:
        key = (spec.direction, spec.header)
        if key in self._specs:
            raise ValueError(f"duplicate packet spec: {spec.direction}:{spec.header}")
        self._specs[key] = spec

    def get(self, direction: str, header: str) -> PacketSpec | None:
        return self._specs.get((direction, header))

    def all(self) -> tuple[PacketSpec, ...]:
        return tuple(self._specs[key] for key in sorted(self._specs))

    def dump(self, path: str | Path) -> None:
        payload = {"version": "1", "packets": [asdict(spec) for spec in self.all()]}
        Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "PacketCatalog":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls([PacketSpec(**item) for item in payload["packets"]])
