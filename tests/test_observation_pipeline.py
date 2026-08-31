from app.client.entity_detection import Detection
from app.client.multi_entity import MultiEntityObservation
from app.runtime.observation_pipeline import ObservationPipeline


def test_observation_pipeline_publishes_world_snapshot():
    events = []
    pipeline = ObservationPipeline(publisher=events.append)
    observation = MultiEntityObservation(
        player=(Detection("player", 10, 20, 20, 30, 0.9),)
    )

    event = pipeline.process(observation, map_id="map-1", correlation_id="corr-1")

    assert event.correlation_id == "corr-1"
    assert event.observation_only is True
    assert event.tick == 1
    assert event.world_state["map_id"] == "map-1"
    assert events == [event]
    assert pipeline.snapshot().character["screen_x"] == 10


def test_observation_pipeline_advances_monotonically():
    pipeline = ObservationPipeline()
    observation = MultiEntityObservation()
    first = pipeline.process(observation)
    second = pipeline.process(observation)

    assert second.tick == first.tick + 1
    assert second.world_state["revision"] == first.world_state["revision"] + 1
