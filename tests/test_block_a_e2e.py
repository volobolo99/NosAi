from app.client.entity_detection import Detection
from app.client.multi_entity import MultiEntityObservation
from app.runtime import ObservationPipeline
from app.world_model import HudValue


def test_block_a_end_to_end_uses_pipeline_for_every_frame():
    events = []
    pipeline = ObservationPipeline(publisher=events.append)

    first = pipeline.process(
        MultiEntityObservation(
            player=(Detection("player", 100, 100, 20, 30, 0.96),),
            mob=(Detection("mob", 180, 120, 30, 30, 0.91),),
        ),
        map_id="nosville", correlation_id="frame-1",
    )
    second = pipeline.process(
        MultiEntityObservation(
            player=(Detection("player", 102, 101, 20, 30, 0.97),),
            mob=(Detection("mob", 185, 123, 30, 30, 0.92),),
        ),
        map_id="nosville", correlation_id="frame-2",
        hud={"hp": HudValue("1500", 0.95), "mp": HudValue("800", 0.90)},
    )

    assert first.observation_only is True
    assert second.observation_only is True
    assert second.tick == first.tick + 1
    assert second.world_state["revision"] == first.world_state["revision"] + 1
    assert second.world_state["map_id"] == "nosville"
    assert second.world_state["character"]["hp"] == 1500
    assert second.world_state["character"]["mp"] == 800
    assert set(second.world_state["entities"]) == set(first.world_state["entities"])
    assert [event.correlation_id for event in events] == ["frame-1", "frame-2"]
