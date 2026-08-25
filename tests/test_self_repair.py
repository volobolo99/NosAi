from pathlib import Path

from app.self_repair import ErrorEvent, RepairCandidate, RepairEngine, RepairPolicy
from app.self_repair.journal import RepairJournal
from app.self_repair.models import FileOperation


def candidate(event_id: str, operation: FileOperation, *, confidence: float = 0.95, risk: float = 0.05) -> RepairCandidate:
    return RepairCandidate(
        candidate_id="candidate-1",
        error_id=event_id,
        hypothesis="controlled test repair",
        operations=(operation,),
        expected_improvement=1.0,
        risk=risk,
        confidence=confidence,
    )


def test_workspace_blocks_path_escape(tmp_path: Path) -> None:
    engine = RepairEngine(tmp_path, RepairJournal(tmp_path / "events.jsonl"))
    event = ErrorEvent("ERR-1", "TEST", "x", "failure")
    operation = FileOperation("create", "../escape.txt", "bad")

    result = engine.handle_error(event, lambda *_: (candidate("ERR-1", operation),))
    assert result.status == "FAILED"
    assert not (tmp_path.parent / "escape.txt").exists()


def test_rejected_candidate_is_rolled_back(tmp_path: Path) -> None:
    target = tmp_path / "app"
    target.mkdir()
    file_path = target / "state.txt"
    file_path.write_text("original", encoding="utf-8")
    journal = RepairJournal(tmp_path / "events.jsonl")
    policy = RepairPolicy(test_commands=(("python", "-c", "raise SystemExit(1)"),))
    engine = RepairEngine(tmp_path, journal, policy)
    event = ErrorEvent("ERR-2", "TEST", "x", "failure")
    operation = FileOperation("modify", "app/state.txt", "broken")

    result = engine.handle_error(event, lambda *_: (candidate("ERR-2", operation),))
    assert result.status == "REJECTED"
    assert file_path.read_text(encoding="utf-8") == "original"


def test_delete_requires_explicit_policy(tmp_path: Path) -> None:
    target = tmp_path / "app"
    target.mkdir()
    file_path = target / "remove.txt"
    file_path.write_text("keep", encoding="utf-8")
    engine = RepairEngine(tmp_path, RepairJournal(tmp_path / "events.jsonl"))
    event = ErrorEvent("ERR-3", "TEST", "x", "failure")
    operation = FileOperation("delete", "app/remove.txt")

    result = engine.handle_error(event, lambda *_: (candidate("ERR-3", operation),))
    assert result.status == "FAILED"
    assert file_path.exists()


def test_low_confidence_candidate_is_blocked(tmp_path: Path) -> None:
    engine = RepairEngine(tmp_path, RepairJournal(tmp_path / "events.jsonl"))
    event = ErrorEvent("ERR-4", "TEST", "x", "failure")
    operation = FileOperation("create", "app/new.txt", "x")

    result = engine.handle_error(event, lambda *_: (candidate("ERR-4", operation, confidence=0.2),))
    assert result.status == "BLOCKED"
