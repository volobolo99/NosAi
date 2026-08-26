"""Optional integrations with external NosTale ecosystem projects."""

from .nostale_ecosystem import (
    EntitySnapshot,
    GameStateSnapshot,
    PacketEnvelope,
    SourceDescriptor,
    normalize_packet,
)

__all__ = [
    "EntitySnapshot",
    "GameStateSnapshot",
    "PacketEnvelope",
    "SourceDescriptor",
    "normalize_packet",
]
