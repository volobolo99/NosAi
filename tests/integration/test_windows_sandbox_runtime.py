from __future__ import annotations

import os

import pytest

from app.simulation_repair.sandbox import SandboxRequest
from app.simulation_repair.windows_sandbox import WindowsSandboxBackend


@pytest.mark.skipif(os.name != "nt", reason="requires a Windows host")
def test_real_windows_sandbox_smoke():
    if os.environ.get("NOSAI_RUN_WINDOWS_SANDBOX") != "1":
        pytest.skip("set NOSAI_RUN_WINDOWS_SANDBOX=1 to run the real disposable sandbox smoke test")
    result = WindowsSandboxBackend().execute(
        SandboxRequest(
            candidate_id="windows-smoke",
            files={"noop.txt": "NosAi sandbox smoke"},
            command=["cmd.exe", "/d", "/c", "echo NOSAI_SANDBOX_OK"],
            timeout_seconds=90,
            network=False,
        )
    )
    assert result.status == "PASS", result.stderr
    assert result.exit_code == 0
    assert "NOSAI_SANDBOX_OK" in result.stdout
    assert result.isolation == "windows-sandbox"
