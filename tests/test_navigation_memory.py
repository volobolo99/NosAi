from app.ai.navigation_memory import NavigationGoal, NavigationMemoryBridge
from app.client.minimap_navigation import GridPoint
from app.client.multi_entity import MinimapObservation


def test_navigation_proposal_is_replayable_and_observation_only():
    bridge = NavigationMemoryBridge()
    minimap = MinimapObservation(detections=(), width=64, height=64)
    plan = bridge.propose(
        minimap,
        GridPoint(0, 0),
        NavigationGoal(GridPoint(2, 1), "npc_goal"),
        state={"map": "test"},
    )
    assert plan is not None
    assert plan.observation_only is True
    latest = bridge.latest()
    assert len(latest) == 1
    assert latest[0].action == "propose_move"
    assert latest[0].info["observation_only"] is True
