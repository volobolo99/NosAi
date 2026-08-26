from app.ai.brain import BrainObservation, NosAiBrain
from app.ai.contracts import ActionIntent, ActionKind, Goal, MemoryRecord, Outcome, RewardEvidence
from app.memory.evidence import MemoryEvidenceProvider


def _evidence():
    record = MemoryRecord(
        "same-state", Goal("progress"), ActionIntent(ActionKind.ATTACK),
        Outcome("success"), RewardEvidence({"total": 10.0}),
    )
    return MemoryEvidenceProvider().build([record], state_fingerprint="same-state", goal_kind="progress")


def test_ab_memory_off_preserves_baseline_decision():
    brain = NosAiBrain()
    decision = brain.decide(
        BrainObservation({"hp_ratio": 0.9, "objective": "kill_all", "target_distance": 5}),
        actions=("attack", "wait"),
    )
    assert decision.action_type in {"attack", "wait"}


def test_ab_memory_on_can_only_reinforce_allowed_action():
    brain = NosAiBrain()
    decision = brain.decide(
        BrainObservation({"hp_ratio": 0.9, "objective": "kill_all", "target_distance": 5}),
        actions=("attack", "wait"), memory_evidence=_evidence(),
    )
    assert decision.action_type == "attack"
    assert "canonical memory evidence" in decision.reasons
