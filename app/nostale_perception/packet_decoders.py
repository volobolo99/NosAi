"""Conservative NosTale packet decoders for high-value state bootstrap packets."""
from __future__ import annotations

from .network_decoder import DecodedObservation
from .network_observation import NetworkObservation


def _tokens(observation: NetworkObservation) -> list[str]:
    return observation.payload.strip().split()


def decode_mv(observation: NetworkObservation) -> DecodedObservation | None:
    tokens = _tokens(observation)
    if len(tokens) < 3:
        return None
    try:
        x, y = float(tokens[0]), float(tokens[1])
        entity_id = int(tokens[2])
    except ValueError:
        return None
    return DecodedObservation(observation.observation_id, "movement", {"x": x, "y": y, "entity_id": entity_id}, 0.55, "mv-v0-unverified")


def decode_in(observation: NetworkObservation) -> DecodedObservation | None:
    tokens = _tokens(observation)
    if not tokens:
        return None
    return DecodedObservation(observation.observation_id, "entity_update", {"tokens": tokens}, 0.30, "in-v0-unverified")


def decode_out(observation: NetworkObservation) -> DecodedObservation | None:
    tokens = _tokens(observation)
    if not tokens:
        return None
    return DecodedObservation(observation.observation_id, "entity_remove_or_update", {"tokens": tokens}, 0.25, "out-v0-unverified")
