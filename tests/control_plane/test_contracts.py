from uuid import UUID

import pytest

from app.control_plane.contracts import (
    InvalidRunTransition,
    RunRecord,
    RunState,
    transition_run,
)


def make_run() -> RunRecord:
    return RunRecord(
        task_id="task-1",
        source="test",
        repository="volobolo99/NosAi",
        ref="main",
    )


def test_run_starts_queued_with_stable_identity() -> None:
    run = make_run()
    assert run.state is RunState.QUEUED
    assert isinstance(run.run_id, UUID)
    assert run.created_at.tzinfo is not None


def test_valid_lifecycle_transition_is_immutable() -> None:
    run = make_run()
    next_run = transition_run(run, RunState.CONTEXT_READY)

    assert run.state is RunState.QUEUED
    assert next_run.state is RunState.CONTEXT_READY
    assert next_run.run_id == run.run_id
    assert next_run.updated_at >= run.updated_at


def test_invalid_transition_cannot_skip_testing() -> None:
    run = make_run()
    run = transition_run(run, RunState.CONTEXT_READY)
    run = transition_run(run, RunState.PLANNED)
    run = transition_run(run, RunState.EXECUTING)

    with pytest.raises(InvalidRunTransition):
        transition_run(run, RunState.PROMOTABLE)


def test_terminal_state_cannot_be_reopened() -> None:
    run = make_run()
    for state in (
        RunState.CONTEXT_READY,
        RunState.PLANNED,
        RunState.EXECUTING,
        RunState.TESTING,
        RunState.VERIFYING,
        RunState.REJECTED,
    ):
        run = transition_run(run, state)

    with pytest.raises(InvalidRunTransition):
        transition_run(run, RunState.QUEUED)


def test_rejection_preserves_reason() -> None:
    run = make_run()
    for state in (
        RunState.CONTEXT_READY,
        RunState.PLANNED,
        RunState.EXECUTING,
        RunState.TESTING,
    ):
        run = transition_run(run, state)

    run = transition_run(run, RunState.REJECTED, reason="deterministic test failed")
    assert run.failure_reason == "deterministic test failed"
