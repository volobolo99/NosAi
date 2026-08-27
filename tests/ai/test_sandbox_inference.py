import time

import pytest

from nosai.ai.sandbox_inference import InferenceSandbox, SandboxError


def test_inference_is_reproducible_and_emits_evidence():
    sandbox = InferenceSandbox()
    out, evidence = sandbox.infer("r1", "baseline", "1.0.0", {"x": 2}, lambda p: {"y": p["x"] * 2})
    assert out == {"y": 4}
    assert evidence.success
    assert len(evidence.input_digest) == 64
    assert len(evidence.output_digest) == 64
    assert len(evidence.digest()) == 64


def test_input_limit_is_enforced():
    sandbox = InferenceSandbox(max_input_bytes=10)
    with pytest.raises(SandboxError, match="input exceeds"):
        sandbox.infer("r1", "m", "1", {"payload": "too large"}, lambda p: p)


def test_failure_is_captured_as_evidence():
    sandbox = InferenceSandbox()
    out, evidence = sandbox.infer("r1", "m", "1", {"x": 1}, lambda p: 1 / 0)
    assert out is None
    assert not evidence.success
    assert evidence.error == "ZeroDivisionError"


def test_timeout_boundary_is_reported():
    sandbox = InferenceSandbox(timeout_seconds=0.001)
    def slow(_):
        time.sleep(0.01)
        return {"ok": True}
    out, evidence = sandbox.infer("r1", "m", "1", {}, slow)
    assert out is None
    assert not evidence.success
    assert evidence.error == "SandboxError"
