"""Structured evidence collection for real Windows sandbox/runtime gates."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True, slots=True)
class WindowsEvidence:
    schema_version: str
    captured_at_utc: str
    host_os: str
    host_release: str
    host_arch: str
    python_version: str
    sandbox_cli: str | None
    sandbox_cli_version: str | None
    sandbox_available: bool
    network_probe: str
    payload_root: str
    payload_sha256: str | None
    command: tuple[str, ...]
    exit_code: int | None
    stdout_sha256: str | None
    stderr_sha256: str | None


def _sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_windows_evidence(
    *, payload_root: Path, command: tuple[str, ...], stdout_path: Path | None = None,
    stderr_path: Path | None = None, exit_code: int | None = None,
) -> WindowsEvidence:
    cli = shutil.which("wsb") if os.name == "nt" else None
    cli_version = None
    if cli:
        try:
            result = subprocess.run([cli, "--version"], capture_output=True, text=True, timeout=10, check=False)
            cli_version = (result.stdout or result.stderr).strip() or None
        except (OSError, subprocess.SubprocessError):
            cli_version = None
    return WindowsEvidence(
        schema_version="1.0",
        captured_at_utc=datetime.now(timezone.utc).isoformat(),
        host_os=platform.system(),
        host_release=platform.release(),
        host_arch=platform.machine(),
        python_version=platform.python_version(),
        sandbox_cli=cli,
        sandbox_cli_version=cli_version,
        sandbox_available=bool(cli),
        network_probe="NOT_PERFORMED",
        payload_root=str(payload_root.resolve()),
        payload_sha256=_sha256(payload_root) if payload_root.is_file() else None,
        command=command,
        exit_code=exit_code,
        stdout_sha256=_sha256(stdout_path) if stdout_path else None,
        stderr_sha256=_sha256(stderr_path) if stderr_path else None,
    )


def write_evidence(evidence: WindowsEvidence, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(asdict(evidence), indent=2, sort_keys=True) + "\n", encoding="utf-8")
