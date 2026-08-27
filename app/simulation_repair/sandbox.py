"""Policy-first sandbox contract for isolated candidate experiments.

The core project never executes arbitrary researched code. A sandbox backend is
injected by the runtime and must explicitly report its isolation boundary.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(slots=True)
class SandboxRequest:
    candidate_id: str
    source_ref: str | None = None
    files: dict[str, str] = field(default_factory=dict)
    command: list[str] = field(default_factory=list)
    timeout_seconds: int = 60
    network: bool = False


@dataclass(slots=True)
class SandboxResult:
    status: str
    exit_code: int | None
    stdout: str
    stderr: str
    evidence: list[str]
    isolation: str


class SandboxBackend(Protocol):
    def execute(self, request: SandboxRequest) -> SandboxResult: ...


class NoOpSandbox:
    """Safe default: refuses execution until a trusted backend is configured."""

    def execute(self, request: SandboxRequest) -> SandboxResult:
        return SandboxResult(
            status="NOT_RUN",
            exit_code=None,
            stdout="",
            stderr="Sandbox backend not configured; no candidate code executed.",
            evidence=[],
            isolation="none",
        )


def _unsafe_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    parts = normalized.split("/")
    return (
        not normalized
        or normalized.startswith("/")
        or normalized.startswith("~")
        or len(normalized) >= 2 and normalized[1] == ":"
        or ".." in parts
    )


def validate_request(request: SandboxRequest) -> list[str]:
    errors: list[str] = []
    if request.timeout_seconds <= 0 or request.timeout_seconds > 900:
        errors.append("timeout_seconds must be between 1 and 900")
    if not request.candidate_id.strip():
        errors.append("candidate_id is required")
    if request.network:
        errors.append("network access must remain disabled for the core sandbox")
    if not request.command:
        errors.append("command is required for an executable sandbox request")
    for path in request.files:
        if _unsafe_path(path):
            errors.append(f"unsafe sandbox path: {path}")
    return errors
