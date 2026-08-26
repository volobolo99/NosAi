from __future__ import annotations

import pytest

from app.nostale_perception.network_decoder import DecodedObservation, DecoderRegistry
from app.nostale_perception.network_observation import NetworkObservation


def _decoder(obs: NetworkObservation) -> DecodedObservation:
    return DecodedObservation(obs.observation_id, "test.event", {"ok": True}, 1.0, "0.1")


def test_registry_decodes_known_header_and_preserves_unknown() -> None:
    registry = DecoderRegistry()
    registry.register("in", _decoder)
    observation = NetworkObservation("o1", 1, "recv", "in", b"x", "fixture", "1")
    assert registry.decode(observation).kind == "test.event"
    unknown = NetworkObservation("o2", 2, "recv", "out", b"x", "fixture", "1")
    assert registry.decode(unknown) is None


def test_registry_rejects_duplicate_header() -> None:
    registry = DecoderRegistry()
    registry.register("in", _decoder)
    with pytest.raises(ValueError):
        registry.register("in", _decoder)
