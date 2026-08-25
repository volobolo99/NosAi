"""Safe repository workspace mutations for the repair engine.

The engine may create, modify, or delete files only under an explicit allowlist.
It always creates a rollback snapshot before mutating the workspace.
"""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from .models import FileOperation


class WorkspacePolicyError(RuntimeError):
    """Raised when a proposed mutation violates workspace policy."""


class RepairWorkspace:
    def __init__(self, root: str | Path, allowed_roots: tuple[str, ...] = ("app", "tests")) -> None:
        self.root = Path(root).resolve()
        self.allowed_roots = tuple(Path(p) for p in allowed_roots)
        self.snapshot_root = self.root / ".nosai-repair" / "snapshots"

    def resolve(self, relative_path: str) -> Path:
        path = Path(relative_path)
        if path.is_absolute() or ".." in path.parts:
            raise WorkspacePolicyError(f"path outside workspace: {relative_path}")
        resolved = (self.root / path).resolve()
        if not any(resolved == (self.root / allowed).resolve() or (self.root / allowed).resolve() in resolved.parents for allowed in self.allowed_roots):
            raise WorkspacePolicyError(f"path not in allowed roots: {relative_path}")
        return resolved

    def snapshot(self, relative_path: str, run_id: str) -> str | None:
        target = self.resolve(relative_path)
        if not target.exists():
            return None
        digest = hashlib.sha256(str(target).encode()).hexdigest()[:16]
        destination = self.snapshot_root / run_id / f"{digest}-{target.name}"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, destination)
        return str(destination.relative_to(self.root))

    def apply(self, operations: tuple[FileOperation, ...], run_id: str) -> list[str]:
        snapshots: list[str] = []
        for op in operations:
            target = self.resolve(op.path)
            snapshot = self.snapshot(op.path, run_id)
            if snapshot:
                snapshots.append(snapshot)
            if op.operation == "delete":
                if target.exists():
                    target.unlink()
                continue
            if op.content is None:
                raise WorkspacePolicyError(f"missing content for {op.operation}: {op.path}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(op.content, encoding="utf-8")
        return snapshots
