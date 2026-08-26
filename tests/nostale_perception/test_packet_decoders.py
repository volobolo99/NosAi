from __future__ import annotations

from app.nostale_perception.network_observation import NetworkObservation
from app.nostale_perception.packet_decoders import decode_in, decode_mv, decode_out


def obs(header: str, payload: bytes) -> NetworkObservation:
    return NetworkObservation("o1", 1, "recv", header, payload, "fixture", "1")


def test_mv_requires_valid_numeric_shape() -> None:
    decoded = decode_mv(obs("mv", b"12.5 8.0 42"))
    assert decoded is not None
    assert decoded.payload["entity_id"] == 42
    assert decode_mv(obs("mv", b"bad")) is None


def test_in_and_out_remain_conservative() -> None:
    assert decode_in(obs("in", b"foo bar")).kind == "entity_update"
    assert decode_out(obs("out", b"42")).kind == "entity_remove_or_update"
