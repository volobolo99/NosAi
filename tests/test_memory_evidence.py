from app.ai.contracts import ActionIntent, ActionKind, Goal, MemoryRecord, Outcome, RewardEvidence
from app.memory.evidence import MemoryEvidenceProvider


def test_memory_evidence_is_advisory_and_empty_when_no_match():
    provider = MemoryEvidenceProvider()
    evidence = provider.build([], state_fingerprint="x", goal_kind="survive")
    assert evidence.matches == ()
    assert evidence.confidence == 0.0


def test_memory_evidence_exposes_ranked_experience():
    record = MemoryRecord(
        "same", Goal("survive"), ActionIntent(ActionKind.RETREAT),
        Outcome("success"), RewardEvidence({"total": 3.0}),
    )
    evidence = MemoryEvidenceProvider().build([record], state_fingerprint="same", goal_kind="survive")
    assert evidence.matches[0].record is record
    assert evidence.confidence > 0
    assert "same_state" in evidence.summary
