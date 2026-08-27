from __future__ import annotations

import os

from app.simulation_repair.sandbox import SandboxRequest, validate_request
from app.simulation_repair.windows_sandbox import WindowsSandboxBackend, _extract_sandbox_id


def test_windows_backend_rejects_network_access():
    request = SandboxRequest(
        candidate_id="candidate",
        files={"main.py": "print('ok')"},
        command=["python", "main.py"],
        network=True,
    )
    result = WindowsSandboxBackend().execute(request)
    assert result.status == "REJECTED"
    assert "network access" in result.stderr


def test_windows_backend_is_not_reported_as_run_on_non_windows():
    if os.name == "nt":
        return
    request = SandboxRequest(
        candidate_id="candidate",
        files={"main.py": "print('ok')"},
        command=["python", "main.py"],
    )
    result = WindowsSandboxBackend().execute(request)
    assert result.status == "NOT_RUN"
    assert result.isolation == "none"


def test_windows_sandbox_id_parser():
    assert _extract_sandbox_id('{"id":"1234"}') == "1234"
    assert _extract_sandbox_id('{"sandboxId":"abcd"}') == "abcd"
    assert _extract_sandbox_id("not-json") is None


def test_existing_sandbox_request_validation_remains_fail_closed():
    errors = validate_request(
        SandboxRequest(candidate_id="", files={"../escape.py": "x"}, command=[])
    )
    assert "candidate_id is required" in errors
    assert "command is required for an executable sandbox request" in errors
    assert any("unsafe sandbox path" in item for item in errors)
