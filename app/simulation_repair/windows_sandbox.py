"""Windows Sandbox backend for disposable, offline candidate execution.

The backend targets Windows Sandbox CLI available on Windows 11 24H2+ and
fails closed when the host cannot provide the required isolation. It maps only
two temporary folders: candidate workspace read-only and an output folder
writable for test artifacts. Network and clipboard are disabled.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Sequence

from .sandbox import SandboxRequest, SandboxResult, validate_request


class WindowsSandboxBackend:
    """Execute a candidate inside Windows Sandbox CLI when available."""

    isolation_name = "windows-sandbox"

    def __init__(self, *, cli: str = "wsb", launch_timeout: int = 120) -> None:
        self.cli = cli
        self.launch_timeout = launch_timeout

    def execute(self, request: SandboxRequest) -> SandboxResult:
        errors = validate_request(request)
        if errors:
            return SandboxResult("REJECTED", None, "", "\n".join(errors), [], "none")
        if os.name != "nt":
            return SandboxResult("NOT_RUN", None, "", "Windows Sandbox requires a Windows host.", [], "none")
        if shutil.which(self.cli) is None:
            return SandboxResult("NOT_RUN", None, "", f"Windows Sandbox CLI '{self.cli}' was not found.", [], "none")

        with tempfile.TemporaryDirectory(prefix="nosai-sandbox-") as temp:
            root = Path(temp)
            work = root / "work"
            out = root / "out"
            work.mkdir()
            out.mkdir()
            for relative, content in request.files.items():
                target = work / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")

            command_line = _windows_command(request.command)
            script = work / "nosai-run.cmd"
            script.write_text(
                "@echo off\n"
                f"{command_line} > C:\\NosAiOut\\stdout.txt 2> C:\\NosAiOut\\stderr.txt\n"
                "echo %ERRORLEVEL% > C:\\NosAiOut\\exit_code.txt\n",
                encoding="utf-8",
            )

            config = (
                "<Configuration>"
                "<VGpu>Disable</VGpu>"
                "<Networking>Disable</Networking>"
                "<ClipboardRedirection>Disable</ClipboardRedirection>"
                "</Configuration>"
            )
            try:
                start = self._run([self.cli, "start", "--raw", "--config", config], self.launch_timeout)
                if start.returncode != 0:
                    return self._failed("Sandbox start failed", start)
                sandbox_id = _extract_sandbox_id(start.stdout)
                if not sandbox_id:
                    return SandboxResult("FAIL", None, start.stdout, "Sandbox ID was not returned.", [], self.isolation_name)

                share_work = self._run(
                    [self.cli, "share", "--id", sandbox_id, "--host-path", str(work), "--sandbox-path", r"C:\NosAiWork"],
                    30,
                )
                if share_work.returncode != 0:
                    return self._failed("Workspace share failed", share_work)
                share_out = self._run(
                    [self.cli, "share", "--id", sandbox_id, "--host-path", str(out), "--sandbox-path", r"C:\NosAiOut", "--allow-write"],
                    30,
                )
                if share_out.returncode != 0:
                    return self._failed("Output share failed", share_out)

                exec_result = self._run(
                    [self.cli, "exec", "--id", sandbox_id, "-c", r"C:\NosAiWork\nosai-run.cmd", "-r", "System", "-d", r"C:\NosAiWork"],
                    max(request.timeout_seconds, 30),
                )
                stdout = _read(out / "stdout.txt")
                stderr = _read(out / "stderr.txt")
                exit_code = _read_int(out / "exit_code.txt")
                evidence = [str(p) for p in sorted(out.iterdir()) if p.is_file()]
                self._run([self.cli, "stop", "--id", sandbox_id], 30)
                status = "PASS" if exec_result.returncode == 0 and exit_code == 0 else "FAIL"
                return SandboxResult(status, exit_code, stdout, stderr, evidence, self.isolation_name)
            except (OSError, subprocess.SubprocessError) as exc:
                return SandboxResult("FAIL", None, "", f"Sandbox backend error: {exc}", [], self.isolation_name)

    def _run(self, args: Sequence[str], timeout: int) -> subprocess.CompletedProcess[str]:
        return subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)

    def _failed(self, detail: str, result: subprocess.CompletedProcess[str]) -> SandboxResult:
        return SandboxResult("FAIL", result.returncode, result.stdout, f"{detail}: {result.stderr}", [], self.isolation_name)


def _windows_command(command: Sequence[str]) -> str:
    return subprocess.list2cmdline(list(command))


def _extract_sandbox_id(raw: str) -> str | None:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if isinstance(data, dict):
        for key in ("id", "sandboxId", "sandbox_id"):
            value = data.get(key)
            if isinstance(value, str) and value:
                return value
    return None


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def _read_int(path: Path) -> int | None:
    try:
        return int(_read(path).strip())
    except (TypeError, ValueError):
        return None
