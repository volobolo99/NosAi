"""Provider-neutral contracts inspired by the NosTale ecosystem.

NosAi does not import ChickenAPI/NosCore/NosSmooth directly.  Instead, external
packet/entity/action data is translated once into these stable contracts.
This keeps the AI runtime independent from a specific emulator or bot stack.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class SourceDescriptor:
    """Provenance for normalized external data."""

    name: str
    repository: str
    license: str | None = None
    version_or_ref: str | None = None


@dataclass(frozen=True)
class PacketEnvelope:
    """Transport-neutral representation of a decoded NosTale packet."""

    name: str
    fields: Mapping[str, Any] = field(default_factory=dict)
    direction: str = "unknown"
    timestamp_ns: int | None = None
    source: SourceDescriptor | None = None


@dataclass(frozen=True)
class EntitySnapshot:
    """Canonical entity view consumed by perception/world layers."""

    entity_id: int | str
    entity_type: str
    x: float | None = None
    y: float | None = None
    hp: int | None = None
    max_hp: int | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GameStateSnapshot:
    """Canonical, immutable game-state boundary for the AI."""

    tick: int
    map_id: int | str | None
    player_id: int | str | None
    entities: tuple[EntitySnapshot, ...] = ()
    values: Mapping[str, Any] = field(default_factory=dict)
    packets: tuple[PacketEnvelope, ...] = ()


def normalize_packet(
    name: str,
    fields: Mapping[str, Any] | None = None,
    *,
    direction: str = "unknown",
    timestamp_ns: int | None = None,
    source: SourceDescriptor | None = None,
) -> PacketEnvelope:
    """Normalize decoded packet data without coupling NosAi to a provider."""

    if not name or not name.strip():
        raise ValueError("packet name must be non-empty")
    if direction not in {"incoming", "outgoing", "unknown"}:
        raise ValueError("direction must be incoming, outgoing, or unknown")
    return PacketEnvelope(
        name=name.strip(),
        fields=dict(fields or {}),
        direction=direction,
        timestamp_ns=timestamp_ns,
        source=source,
    )
