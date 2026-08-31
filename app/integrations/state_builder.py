"""Build CanonicalGameState from already-normalized observations.

This layer deliberately does not parse client memory or inject into the game.
Providers feed normalized observations into this deterministic reducer.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Any, Mapping

from .canonical_state import CanonicalGameState, EntityState, PlayerState


def build_state(
    *,
    timestamp_ms: int,
    client_pid: int | None,
    observation: Mapping[str, Any],
    sequence: int = 0,
    frame_sha256: str | None = None,
) -> CanonicalGameState:
    player_raw = observation.get("player") or {}
    player = PlayerState(
        entity_id=player_raw.get("entity_id"),
        x=_number(player_raw.get("x")),
        y=_number(player_raw.get("y")),
        hp=_int(player_raw.get("hp")),
        max_hp=_int(player_raw.get("max_hp")),
        mp=_int(player_raw.get("mp")),
        max_mp=_int(player_raw.get("max_mp")),
        direction=_int(player_raw.get("direction")),
        target_id=player_raw.get("target_id"),
    )

    entities: list[EntityState] = []
    for raw in observation.get("entities") or []:
        if not raw.get("entity_id") or not raw.get("kind"):
            continue
        entities.append(
            EntityState(
                entity_id=str(raw["entity_id"]),
                kind=str(raw["kind"]),
                x=_number(raw.get("x")),
                y=_number(raw.get("y")),
                hp=_int(raw.get("hp")),
                mp=_int(raw.get("mp")),
                name=raw.get("name"),
                target_id=raw.get("target_id"),
                source=str(raw.get("source", "unknown")),
            )
        )

    quality = _quality(player, entities, observation)
    return CanonicalGameState(
        timestamp_ms=timestamp_ms,
        client_pid=client_pid,
        map_id=observation.get("map_id"),
        player=player,
        entities=tuple(entities),
        packets_observed=_int(observation.get("packets_observed")) or 0,
        frame_sha256=frame_sha256,
        sources=tuple(str(x) for x in observation.get("sources", ()) if x),
        quality=quality,
        sequence=sequence,
    )


def _quality(player: PlayerState, entities: list[EntityState], observation: Mapping[str, Any]) -> float:
    checks = [player.x is not None and player.y is not None, bool(observation.get("map_id"))]
    checks.append(bool(entities) or observation.get("entities") == [])
    return round(sum(checks) / len(checks), 3)


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None
