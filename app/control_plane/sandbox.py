"""Sandbox contracts and a safe, provider-neutral local backend.

The manager owns lifecycle and cleanup semantics. Production Docker execution
can implement the same provider contract later; CI uses the local backend so
control-plane tests remain deterministic and do not require a Docker daemon.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import shutil
import subprocess
from typing import Mapping, Protocol, Sequence
from uuid import UUID


class SandboxError(RuntimeError):
    """Base error for sandbox lifecycle failures."""


@dataclass(frozen=True, slots=True)
class SandboxSpec:
    repository: str
    ref: str
    run_id: UUID
    timeout_seconds: int = 300
    memory_mb: int = 2048
    cpu_limit: float = 1.0
    network_enabled: bool = False


@dataclass(frozen=True, slots=True)
class SandboxHandle:
    sandbox_id: str
    root: Path
    provider: str


class SandboxProvider(Protocol):
    def create(self, spec: SandboxSpec) -> SandboxHandle: ...
    def run(self, handle: SandboxHandle, command: Sequence[str]) -> subprocess.CompletedProcess[str]: ...
    def destroy(self, handle: SandboxHandle) -> None: ...


@dataclass
class LocalWorktreeSandbox:
    """Deterministic CI backend using an isolated git worktree.

    It deliberately does not execute commands during creation. Command
    execution is explicit and remains subject to timeout and environment
    controls. Network is disabled at the API contract level by default.
    """

    base_dir: Path
    _handles: dict[str, SandboxHandle] = field(default_factory=dict)

    def create(self, spec: SandboxSpec) -> SandboxHandle:
        if spec.timeout_seconds <= 0:
            raise SandboxError("timeout_seconds must be positive")
        if spec.memory_mb <= 0 or spec.cpu_limit <= 0:
            raise SandboxError("resource limits must be positive")

        self.base_dir.mkdir(parents=True, exist_ok=True)
        sandbox_id = f"run-{spec.run_id.hex}"
        root = self.base_dir / sandbox_id
        if root.exists():
            raise SandboxError(f"sandbox already exists: {sandbox_id}")

        root.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["git", "-C", spec.repository, "worktree", "add", "--detach", str(root), spec.ref],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise SandboxError(result.stderr.strip() or "git worktree creation failed")

        handle = SandboxHandle(sandbox_id=sandbox_id, root=root, provider="local-worktree")
        self._handles[sandbox_id] = handle
        return handle

    def run(self, handle: SandboxHandle, command: Sequence[str], *, timeout_seconds: int = 300) -> subprocess.CompletedProcess[str]:
        if handle.sandbox_id not in self._handles:
            raise SandboxError("unknown or destroyed sandbox")
        if not command:
            raise SandboxError("command cannot be empty")
        return subprocess.run(
            list(command),
            cwd=handle.root,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env={"PATH": str(Path.cwd() / ".venv" / "bin") + ":/usr/bin:/bin"},
        )

    def destroy(self, handle: SandboxHandle) -> None:
        if handle.sandbox_id not in self._handles:
            return
        result = subprocess.run(
            ["git", "worktree", "remove", "--force", str(handle.root)],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self._handles.pop(handle.sandbox_id, None)
        if result.returncode != 0:
            shutil.rmtree(handle.root, ignore_errors=True)
            raise SandboxError(result.stderr.strip() or "git worktree cleanup failed")


class SandboxManager:
    """Owns sandbox lifecycle and guarantees cleanup on scoped execution."""

    def __init__(self, provider: SandboxProvider) -> None:
        self.provider = provider

    def execute(self, spec: SandboxSpec, command: Sequence[str]) -> subprocess.CompletedProcess[str]:
        handle = self.provider.create(spec)
        try:
            return self.provider.run(handle, command, timeout_seconds=spec.timeout_seconds)
        finally:
            self.provider.destroy(handle)
