from app.ai.brain import BrainObservation, NosAiBrain
from app.ai.contracts import ActionIntent, ActionKind, Goal, MemoryRecord, Outcome, RewardEvidence
from app.memory.evidence import MemoryEvidenceProvider


def test_canonical_memory_is_advisory_and_cannot_create_disallowed_action():
    record = MemoryRecord("state-a", Goal("survive"), ActionIntent(ActionKind.ATTACK), Outcome("success"), RewardEvidence({"total": 10.0}))
    evidence = MemoryEvidenceProvider().build([record], state_fingerprint="state-a", goal_kind="survive")
    decision = NosAiBrain().decide(BrainObservation({"hp_ratio": 0.1, "objective": "survival"}), actions=("heal", "retreat"), memory_evidence=evidence)
    assert decision.action_type in {"heal", "retreat"}
    assert "attack" not in {candidate.action_type for candidate in decision.candidates}


def test_memory_evidence_can_support_an_already_allowed_action():
    record = MemoryRecord("state-b", Goal("progress"), ActionIntent(ActionKind.ATTACK), Outcome("success"), RewardEvidence({"total": 5.0}))
    evidence = MemoryEvidenceProvider().build([record], state_fingerprint="state-b", goal_kind="progress")
    decision = NosAiBrain().decide(BrainObservation({"hp_ratio": 0.9, "objective": "kill_all", "target_distance": 5}), actions=("attack", "wait"), memory_evidence=evidence)
    assert decision.action_type == "attack"
    assert "canonical memory evidence" in decision.reasons
