from app.progression.bridge import PlayAiGuardAiBridge, PlayAiProposal
from app.progression.models import CharacterSnapshot, ProgressionPlan


def snapshot():
    return CharacterSnapshot(
        snapshot_id="test", timestamp=1.0, server="test", channel="1", level=10,
        stats={}, equipment={}, specialist={}, skills={}, resistances={},
        resources={}, inventory={}, activity={}, objectives=("target",),
        progression_milestones={}, derived={}, confidence=0.9, provenance="test",
    )


def test_bridge_never_authorizes_execution():
    plan = ProgressionPlan(
        plan_id="p1", description="safe", steps=(), expected_progress=1.0,
        expected_time_s=10.0, resource_cost=0.0, risk=0.1, policy_status="PASS",
    )
    result = PlayAiGuardAiBridge().evaluate(snapshot(), PlayAiProposal("target", (plan,)))
    assert result["producer"] == "PlayAi"
    assert result["supervisor"] == "GuardAi"
    assert result["execution_authorized"] is False
    assert result["evaluation"] is not None
