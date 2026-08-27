from app.progression.bridge import PlayAiGuardAiBridge, PlayAiProposal
from app.progression.models import ProgressionPlan
from app.progression.world_state_adapter import snapshot_from_world_state


def test_progression_pipeline_world_state_to_guardai():
    world_state = {
        "snapshot_id": "e2e-1",
        "timestamp": 1,
        "server": "EU",
        "channel": "1",
        "character": {
            "level": 99,
            "class": "mage",
            "stats": {"attack": 10},
            "resistances": {"fire": 20},
        },
        "resources": {"gold": 1000},
        "inventory": {"ore": 3},
        "objectives": ["reach-target"],
        "confidence": 0.9,
    }
    snapshot = snapshot_from_world_state(world_state, source="e2e-fixture")
    plan = ProgressionPlan(
        plan_id="p-e2e",
        description="baseline progression",
        steps=("farm", "upgrade"),
        expected_progress=1.0,
        expected_time_s=600.0,
        resource_cost=100.0,
        risk=0.1,
        policy_status="PASS",
        evidence=("fixture",),
    )
    result = PlayAiGuardAiBridge().evaluate(
        snapshot,
        PlayAiProposal("reach-target", (plan,), "PlayAi baseline proposal"),
    )
    assert result["producer"] == "PlayAi"
    assert result["supervisor"] == "GuardAi"
    assert result["objective"] == "reach-target"
    assert result["execution_authorized"] is False
    assert result["evaluation"] is not None
