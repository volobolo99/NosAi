from __future__ import annotations

from app.nostale_perception.network_decoder import DecoderRegistry
from app.nostale_perception.network_observation import NetworkObservation
from app.nostale_perception.packet_decoders import decode_mv
from app.nostale_perception.replay_validation import validate_replay


def test_replay_validation_builds_world_model() -> None:
    registry = DecoderRegistry()
    registry.register("mv", decode_mv)
    observations = [
        NetworkObservation("o1", 1, "recv", "mv", b"10 20 42", "fixture", "1"),
        NetworkObservation("o2", 2, "recv", "unknown", b"x", "fixture", "1"),
    ]
    result, model = validate_replay(observations, registry)
    assert result.total == 2
    assert result.decoded == 1
    assert result.unknown == 1
    assert result.applied == 1
    assert model.entities[42].x == 10.0
    assert model.entities[42].y == 20.0
