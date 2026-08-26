from app.client.minimap_navigation import GridPoint, MinimapPathPlanner, astar
from app.client.multi_entity import Detection, MinimapObservation


def test_astar_routes_around_blocked_cell():
    plan = astar(
        GridPoint(0, 0),
        GridPoint(2, 0),
        {GridPoint(1, 0)},
        3,
        3,
    )
    assert plan is not None
    assert GridPoint(1, 0) not in plan.points
    assert plan.observation_only is True


def test_minimap_nearest_entity():
    minimap = MinimapObservation(
        0, 0, 100, 100,
        detections=(
            Detection("mob", 10, 10, 4, 4, 0.9),
            Detection("npc", 80, 80, 4, 4, 0.95),
        ),
    )
    found = MinimapPathPlanner().nearest_entity(minimap, 11, 11, "mob")
    assert found is not None
    assert found.kind == "mob"


def test_blocked_goal_is_not_planned():
    plan = astar(GridPoint(0, 0), GridPoint(1, 0), {GridPoint(1, 0)}, 2, 1)
    assert plan is None
