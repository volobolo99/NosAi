"""Versioned registry contracts for models, policies, strategies and knowledge."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json


@dataclass(frozen=True, slots=True)
class RegistryEntry:
    entry_id: str
    kind: str
    version: str
    parent: str | None
    source_commit: str
    run_id: str
    replay_snapshot: str
    environment: str
    metrics: dict[str, float]
    validation: str
    provenance: tuple[str, ...]
    rollback_target: str | None = None


class VersionRegistry:
    """Local append-only registry; promotion remains a separate governance step."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def register(self, entry: RegistryEntry) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(entry), sort_keys=True, ensure_ascii=True) + "\n")

    def list(self, kind: str | None = None) -> list[RegistryEntry]:
        if not self.path.exists():
            return []
        result: list[RegistryEntry] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    data = json.loads(line)
                    # JSON has no tuple type; restore the RegistryEntry contract
                    # explicitly so persisted entries round-trip losslessly.
                    data["provenance"] = tuple(data.get("provenance", ()))
                    entry = RegistryEntry(**data)
                    if kind is None or entry.kind == kind:
                        result.append(entry)
        return result

    def latest(self, kind: str) -> RegistryEntry | None:
        entries = self.list(kind)
        return entries[-1] if entries else None
