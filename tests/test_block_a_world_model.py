from app.client.entity_detection import Detection
from app.client.multi_entity import MultiEntityObservation
from app.world_model import ObservationMapper, WorldAction, WorldModel, WorldState


def test_world_state_copy_isolated_and_serializable():
    state = WorldState(character={"hp": 100}, flags={"safe": True})
    clone = state.copy()
    clone.character["hp"] = 50
    clone.flags["safe"] = False

    assert state.character["hp"] == 100
    assert state.flags["safe"] is True
    assert state.to_dict()["tick"] == 0


def test_world_model_supported_transitions_are_deterministic_and_non_mutating():
    state = WorldState(map_id="nosville")
    model = WorldModel()

    updated = model.apply(
        state,
        WorldAction("1", "set_flag", {"key": "danger", "value": False}),
    )

    assert state.flags == {}
    assert updated.flags["danger"] is False
    assert updated.revision == 1
    assert updated.source == "simulation"


def test_world_model_fails_closed_on_unknown_action():
    try:
        WorldModel().apply(WorldState(), WorldAction("1", "attack", {}))
    except ValueError as exc:
        assert "unsupported world action" in str(exc)
    else:
        raise AssertionError("unknown world action must fail closed")


def test_observation_mapper_fuses_entities_and_player():
    player = Detection("player", 100, 120, 24, 32, 0.95, source="verified_template")
    mob = Detection("mob", 180, 130, 30, 30, 0.88, source="verified_template")
    observation = MultiEntityObservation(player=(player,), mob=(mob,))

    state = ObservationMapper().update(None, observation, map_id="nosville")

    assert state.map_id == "nosville"
    assert state.source == "visual_perception"
    assert state.character["screen_x"] == 100
    assert state.character["vision_confidence"] == 0.95
    assert len(state.entities) == 2
    assert all(entity.last_seen_tick == 1 for entity in state.entities.values())


def test_observation_mapper_rejects_time_regression():
    previous = WorldState(tick=5)
    observation = MultiEntityObservation()
    try:
        ObservationMapper().update(previous, observation, tick=4)
    except ValueError as exc:
        assert "cannot move backwards" in str(exc)
    else:
        raise AssertionError("observation time regression must fail")
