"""Read-only World State -> CharacterSnapshot adapter."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from .models import CharacterSnapshot


def snapshot_from_world_state(world_state: Mapping[str, Any], *, source: str = "world_state") -> CharacterSnapshot:
    """Normalize known world-state fields without inventing missing game facts."""
    character = dict(world_state.get("character") or {})
    progression = dict(world_state.get("progression") or {})
    resources = dict(world_state.get("resources") or {})
    activity = dict(world_state.get("activity") or {})
    objectives = tuple(str(x) for x in (world_state.get("objectives") or ()))

    return CharacterSnapshot(
        snapshot_id=str(world_state.get("snapshot_id") or "world-state"),
        schema_version="1.0",
        timestamp=str(world_state.get("timestamp") or datetime.now(timezone.utc).isoformat()),
        server=str(world_state.get("server")) if world_state.get("server") is not None else None,
        channel=str(world_state.get("channel")) if world_state.get("channel") is not None else None,
        character_level=_int_or_none(character.get("level")),
        character_class=str(character.get("class")) if character.get("class") is not None else None,
        base_stats=_mapping(character.get("base_stats")),
        effective_stats=_mapping(character.get("effective_stats")),
        equipment=_mapping(character.get("equipment")),
        specialist=_mapping(character.get("specialist")),
        skills=_mapping(character.get("skills")),
        resistances=_mapping(character.get("resistances")),
        resources=resources,
        activity=activity,
        objectives=objectives,
        progression_milestones=_mapping(progression.get("milestones")),
        derived=_mapping(world_state.get("derived")),
        confidence=float(world_state.get("confidence", 0.0) or 0.0),
        provenance=source,
    )


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}
