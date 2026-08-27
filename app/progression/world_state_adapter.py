"""Read-only World State -> CharacterSnapshot adapter."""
from __future__ import annotations

from time import time
from typing import Any, Mapping

from .models import CharacterSnapshot


def snapshot_from_world_state(world_state: Mapping[str, Any], *, source: str = "world_state") -> CharacterSnapshot:
    """Normalize known fields; missing game facts remain missing."""
    character = _mapping(world_state.get("character"))
    progression = _mapping(world_state.get("progression"))
    return CharacterSnapshot(
        snapshot_id=str(world_state.get("snapshot_id") or "world-state"),
        timestamp=_timestamp(world_state.get("timestamp")),
        server=_str_or_none(world_state.get("server")),
        channel=_str_or_none(world_state.get("channel")),
        level=_int_or_none(character.get("level")),
        character_class=_str_or_none(character.get("class")),
        progression_milestones=_mapping(progression.get("milestones")),
        stats=_mapping_number(character.get("stats")),
        equipment=_mapping(character.get("equipment")),
        specialist=_mapping(character.get("specialist")),
        skills=_mapping(character.get("skills")),
        resistances=_mapping_number(character.get("resistances")),
        objectives=tuple(str(x) for x in (world_state.get("objectives") or ())),
        resources=_mapping_number(world_state.get("resources")),
        inventory=_mapping_number(world_state.get("inventory")),
        activity=_mapping(world_state.get("activity")),
        derived=_mapping_number(world_state.get("derived")),
        confidence=float(world_state.get("confidence", 0.0) or 0.0),
        provenance=source,
    )


def _timestamp(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return time()


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _str_or_none(value: Any) -> str | None:
    return str(value) if value is not None else None


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _mapping_number(value: Any) -> dict[str, float]:
    if not isinstance(value, Mapping):
        return {}
    out: dict[str, float] = {}
    for key, item in value.items():
        try:
            out[str(key)] = float(item)
        except (TypeError, ValueError):
            continue
    return out
