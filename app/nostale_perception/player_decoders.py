"""Conservative bootstrap decoders for player information and conditions."""
from __future__ import annotations

from .network_decoder import DecodedObservation
from .network_observation import NetworkObservation


def _tokens(observation: NetworkObservation) -> list[str]:
    return observation.payload.decode("utf-8", errors="replace").strip().split()


def decode_c_info(observation: NetworkObservation) -> DecodedObservation | None:
    tokens = _tokens(observation)
    if len(tokens) < 5:
        return None
    try:
        entity_id, hp, hp_max, mp, mp_max = map(int, tokens[:5])
    except ValueError:
        return None
    if min(hp, hp_max, mp, mp_max) < 0 or hp > hp_max or mp > mp_max:
        return None
    return DecodedObservation(observation.observation_id, "player_info", {
        "entity_id": entity_id, "hp": hp, "hp_max": hp_max, "mp": mp, "mp_max": mp_max,
    }, 0.45, "c_info-v0-unverified")


def decode_cond(observation: NetworkObservation) -> DecodedObservation | None:
    tokens = _tokens(observation)
    if not tokens:
        return None
    return DecodedObservation(observation.observation_id, "player_condition", {"condition": tokens[0]}, 0.35, "cond-v0-unverified")
