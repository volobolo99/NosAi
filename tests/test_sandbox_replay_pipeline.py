from __future__ import annotations

import json

import pytest

from app.regression.anti_forgetting import verify_retention
from app.regression.sandbox_replay_runner import (
    SandboxReplayRunner,
    UnvalidatedCandidateError,
)


def test_sandbox_replay_passes_protected_metrics(tmp_path):
    session = tmp_path / "session.json"
    session.write_text(
        json.dumps(
            {
                "sandbox_available": True,
                "baseline_metrics": {"task_a": 1.0, "task_b": 0.8},
                "candidate_metrics": {"task_a": 0.99, "task_b": 0.79},
            }
        ),
        encoding="utf-8",
    )

    result = SandboxReplayRunner().run_candidate_replay("candidate-1", str(session))

    assert result.status == "PASS"
    assert result.regressions == ("task_a", "task_b")


def test_sandbox_unavailable_is_unvalidated(tmp_path):
    session = tmp_path / "session.json"
    session.write_text(json.dumps({"sandbox_available": False}), encoding="utf-8")

    with pytest.raises(UnvalidatedCandidateError):
        SandboxReplayRunner().run_candidate_replay("candidate-2", str(session))


def test_missing_replay_is_unvalidated(tmp_path):
    with pytest.raises(UnvalidatedCandidateError):
        SandboxReplayRunner().run_candidate_replay("candidate-3", str(tmp_path / "missing.json"))


def test_anti_forgetting_rejects_excessive_degradation():
    assert verify_retention({"old": 0.90}, {"old": 1.0}, 0.05) is False


def test_anti_forgetting_accepts_small_degradation():
    assert verify_retention({"old": 0.96}, {"old": 1.0}, 0.05) is True
