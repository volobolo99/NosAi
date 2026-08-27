from app.progression.bridge import PlayAiGuardAiBridge, PlayAiProposal
from app.progression.models import CharacterSnapshot, ProgressionPlan


def snapshot():
    return CharacterSnapshot(
        snapshot_id="test", schema_version="1.0", timestamp="2026-01-01T00:00:00Z",
        server="test", channel="1", character_level=10,
        base_stats={}, effective_stats={}, equipment={}, specialist={}, skills={},
        resistances={}, resources={}, activity={}, objectives=("target",),
        progression_milestones={}, derived={}, confidence=0.9, provenance="test",
    )


def test_bridge_never_authorizes_execution():
    plan = ProgressionPlan(id="p1", name="baseline", description="safe", steps=(),
                           expected_progress=1.0, expected_time_minutes=10,
                           resource_cost=0.0, risk=0.1, policy_status="VALID")
    result = PlayAiGuardAiBridge().evaluate(snapshot(), PlayAiProposal("target", (plan,)))
    assert result["producer"] == "PlayAi"
    assert result["supervisor"] == "GuardAi"
    assert result["execution_authorized"] is False
