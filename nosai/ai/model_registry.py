"""Offline, integrity-first model registry for G3.23."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Literal

Lifecycle = Literal["candidate", "validated", "promoted", "retired"]
_ALLOWED: dict[Lifecycle, set[Lifecycle]] = {
    "candidate": {"validated", "retired"},
    "validated": {"promoted", "retired"},
    "promoted": {"retired"},
    "retired": set(),
}


@dataclass(frozen=True)
class ModelManifest:
    model_id: str
    version: str
    artifact_sha256: str
    artifact_size: int
    dataset_digest: str
    evaluation_digest: str
    schema_version: str = "1"
    runtime_compatibility: str = "sandbox-only"
    lifecycle: Lifecycle = "candidate"

    def canonical(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))

    def digest(self) -> str:
        return sha256(self.canonical().encode()).hexdigest()


class ModelRegistry:
    """Filesystem-backed registry; never executes or loads model artifacts."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def register(self, manifest: ModelManifest) -> ModelManifest:
        self._validate(manifest)
        path = self._path(manifest.model_id, manifest.version)
        if path.exists():
            raise ValueError("model version already registered")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(manifest.canonical() + "\n", encoding="utf-8")
        return manifest

    def get(self, model_id: str, version: str) -> ModelManifest:
        path = self._path(model_id, version)
        if not path.exists():
            raise KeyError(f"model not found: {model_id}@{version}")
        data = json.loads(path.read_text(encoding="utf-8"))
        manifest = ModelManifest(**data)
        self._validate(manifest)
        return manifest

    def transition(self, model_id: str, version: str, target: Lifecycle) -> ModelManifest:
        current = self.get(model_id, version)
        if target not in _ALLOWED[current.lifecycle]:
            raise ValueError(f"invalid lifecycle transition: {current.lifecycle} -> {target}")
        updated = ModelManifest(**{**asdict(current), "lifecycle": target})
        self._validate(updated)
        self._path(model_id, version).write_text(updated.canonical() + "\n", encoding="utf-8")
        return updated

    def verify(self, model_id: str, version: str, artifact: bytes) -> bool:
        manifest = self.get(model_id, version)
        return sha256(artifact).hexdigest() == manifest.artifact_sha256 and len(artifact) == manifest.artifact_size

    def _path(self, model_id: str, version: str) -> Path:
        safe_id, safe_version = model_id.replace("/", "_"), version.replace("/", "_")
        return self.root / safe_id / f"{safe_version}.json"

    @staticmethod
    def _validate(manifest: ModelManifest) -> None:
        if not manifest.model_id or not manifest.version:
            raise ValueError("model_id and version are required")
        if len(manifest.artifact_sha256) != 64 or any(c not in "0123456789abcdef" for c in manifest.artifact_sha256.lower()):
            raise ValueError("artifact_sha256 must be a SHA-256 hex digest")
        if manifest.artifact_size < 0:
            raise ValueError("artifact_size must be non-negative")
        if not manifest.dataset_digest or not manifest.evaluation_digest:
            raise ValueError("dataset and evaluation lineage are required")
