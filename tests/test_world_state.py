from app.world_model.world_state import WorldState


def test_entity_observation_creates_and_updates_state():
    world = WorldState()
    first = world.observe_entity(42, {"x": 10, "y": 20, "hp_percent": 100}, sequence=1)
    second = world.observe_entity(42, {"x": 11}, sequence=2)
    assert first.entity_id == 42
    assert second.x == 11
    assert second.y == 20
    assert second.hp_percent == 100
    assert world.sequence == 2


def test_remove_entity_is_idempotent():
    world = WorldState()
    world.observe_entity(42, {}, sequence=1)
    assert world.remove_entity(42, sequence=2) is True
    assert world.remove_entity(42, sequence=3) is False
    assert world.entities == {}
