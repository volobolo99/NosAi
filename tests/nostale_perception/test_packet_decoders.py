from __future__ import annotations

from app.nostale_perception.network_observation import NetworkObservation
from app.nostale_perception.packet_decoders import decode_in, decode_mv, decode_out


def obs(header: str, payload: str) -> NetworkObservation:
    return NetworkObservation(1, "recv", header, payload, "fixture", 1)


def test_mv_requires_valid_numeric_shape() -> None:
    decoded = decode_mv(obs("mv", "12.5 8.0 42"))
    assert decoded is not None
    assert decoded.payload["entity_id"] == 42
    assert decode_mv(obs("mv", "bad")) is None


def test_in_and_out_remain_conservative() -> None:
    assert decode_in(obs("in", "foo bar")).kind == "entity_update"
    assert decode_out(obs("out", "42")).kind == "entity_remove_or_update"
