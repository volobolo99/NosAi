from pathlib import Path
from uuid import uuid4

import pytest

from app.control_plane.sandbox import LocalWorktreeSandbox, SandboxError, SandboxManager, SandboxSpec


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    import subprocess

    subprocess.run(["git", "-C", str(repo), "init"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "nosai@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "NosAi Test"], check=True)
    (repo / "sample.txt").write_text("safe\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "sample.txt"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "init"], check=True, capture_output=True)
    return repo


def test_create_run_and_destroy(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    provider = LocalWorktreeSandbox(tmp_path / "sandboxes")
    manager = SandboxManager(provider)
    spec = SandboxSpec(repository=str(repo), ref="HEAD", run_id=uuid4())

    result = manager.execute(spec, ["/bin/sh", "-c", "cat sample.txt"])

    assert result.returncode == 0
    assert result.stdout == "safe\n"
    assert not (tmp_path / "sandboxes" / f"run-{spec.run_id.hex}").exists()


def test_invalid_limits_are_rejected(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    provider = LocalWorktreeSandbox(tmp_path / "sandboxes")
    with pytest.raises(SandboxError):
        provider.create(SandboxSpec(repository=str(repo), ref="HEAD", run_id=uuid4(), timeout_seconds=0))


def test_unknown_sandbox_cannot_execute(tmp_path: Path) -> None:
    provider = LocalWorktreeSandbox(tmp_path / "sandboxes")
    from app.control_plane.sandbox import SandboxHandle

    with pytest.raises(SandboxError):
        provider.run(SandboxHandle("missing", tmp_path, "test"), ["/bin/true"])
