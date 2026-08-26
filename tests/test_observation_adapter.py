from app.world_model.observation_adapter import apply_observation
from app.world_model.world_state import WorldState


def test_in_and_mv_update_same_entity():
    world = WorldState()
    assert apply_observation(world, {"event": "in", "entity_id": 7, "fields": {"x": 1, "y": 2}}, 1) == "updated"
    assert apply_observation(world, {"event": "mv", "entity_id": 7, "fields": {"x": 5}}, 2) == "updated"
    assert world.entities[7].x == 5
    assert world.entities[7].y == 2


def test_out_removes_entity():
    world = WorldState()
    apply_observation(world, {"event": "in", "entity_id": 7, "fields": {}}, 1)
    assert apply_observation(world, {"event": "out", "entity_id": 7}, 2) == "removed"
    assert 7 not in world.entities


def test_unknown_event_is_not_guessed():
    world = WorldState()
    assert apply_observation(world, {"event": "future_packet", "entity_id": 7}, 1) == "ignored"
    assert world.entities == {}
