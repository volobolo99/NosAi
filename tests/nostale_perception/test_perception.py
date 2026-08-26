from app.nostale_perception.perception import Frame, ObservationPipeline


class FakeSource:
    def capture(self):
        return Frame(frame_id="frame:1", timestamp_ms=1234, width=640, height=480, pixels=b"pixels", source="test")


def test_pipeline_creates_observation_and_gamestate():
    pipeline = ObservationPipeline(
        FakeSource(),
        player_detector=lambda _frame: {"hp": 90, "hp_max": 100, "x": 12.5, "y": 4.0, "confidence": 0.95},
        entity_detector=lambda _frame: [
            {"entity_id": "mob:1", "entity_type": "mob", "x": 14.0, "y": 4.5, "hostile": True, "confidence": 0.8}
        ],
        map_detector=lambda _frame: "map:test",
        ui_detector=lambda _frame: {"inventory_open": False},
    )

    result = pipeline.observe(client_pid=123, window_rect={"left": 1, "top": 2, "right": 641, "bottom": 482})

    assert result.observation.observation_id == "frame:1"
    assert result.observation.data["frame_sha256"]
    assert result.game_state.client_pid == 123
    assert result.game_state.map_name == "map:test"
    assert result.game_state.player.hp == 90
    assert result.game_state.entities[0].hostile is True
    assert result.game_state.overall_confidence == 0.875


def test_pipeline_does_not_invent_missing_perception():
    result = ObservationPipeline(FakeSource()).observe()
    assert result.game_state.player.hp is None
    assert result.game_state.player.x is None
    assert result.game_state.map_name is None
    assert result.game_state.entities == ()
    assert result.game_state.overall_confidence == 0.0
