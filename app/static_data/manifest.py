from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class StaticDataset:
    name: str
    required: bool
    source: str | None
    version: str | None
    sha256: str | None


@dataclass(frozen=True)
class StaticManifest:
    schema_version: int
    project: str
    snapshot_policy: str
    datasets: tuple[StaticDataset, ...]

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "StaticManifest":
        if payload.get("schema_version") != 1:
            raise ValueError("unsupported static-data manifest schema")
        if payload.get("project") != "NosAi":
            raise ValueError("invalid static-data manifest project")
        raw = payload.get("datasets")
        if not isinstance(raw, dict):
            raise ValueError("manifest.datasets must be an object")
        datasets = tuple(
            StaticDataset(
                name=name,
                required=bool(meta.get("required", False)),
                source=meta.get("source"),
                version=meta.get("version"),
                sha256=meta.get("sha256"),
            )
            for name, meta in sorted(raw.items())
            if isinstance(meta, dict)
        )
        if not datasets:
            raise ValueError("manifest contains no datasets")
        return cls(
            schema_version=1,
            project="NosAi",
            snapshot_policy=str(payload.get("snapshot_policy", "immutable-runtime")),
            datasets=datasets,
        )
