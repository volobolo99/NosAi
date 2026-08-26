from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.control_plane import (
    InvalidRunTransition,
    RunRecord,
    RunState,
    transition_run,
)


def make_run() -> RunRecord:
    now = datetime.now(timezone.utc)
    return RunRecord(
        task_id="task-1",
        source="test",
        repository="volobolo99/NosAi",
        ref="main",
        run_id=uuid4(),
        created_at=now,
        updated_at=now,
    )


def test_run_follows_explicit_lifecycle():
    run = make_run()
    for state in (
        RunState.CONTEXT_READY,
        RunState.PLANNED,
        RunState.EXECUTING,
        RunState.TESTING,
        RunState.VERIFYING,
        RunState.EVALUATING,
        RunState.PROMOTABLE,
    ):
        run = transition_run(run, state)
        assert run.state is state


def test_run_cannot_skip_lifecycle_states():
    run = make_run()
    with pytest.raises(InvalidRunTransition):
        transition_run(run, RunState.EXECUTING)


def test_terminal_state_cannot_be_reopened():
    run = make_run()
    run = transition_run(run, RunState.BLOCKED, reason="policy")
    assert run.failure_reason == "policy"
    with pytest.raises(InvalidRunTransition):
        transition_run(run, RunState.QUEUED)


def test_run_records_are_immutable():
    run = make_run()
    with pytest.raises(AttributeError):
        run.state = RunState.BLOCKED
