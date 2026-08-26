"""Conservative mapping boundary for NosCore packet observations.

Packet-specific field mappings are intentionally data-driven: until an actual
packet capture/schema is available, unknown packets are preserved as metadata
rather than guessed into game state.
"""
from __future__ import annotations

from typing import Any, Mapping


KNOWN_PLAYER_FIELDS = frozenset({"entity_id", "x", "y", "hp", "max_hp", "mp", "max_mp", "direction", "target_id"})


def normalize_packet(packet: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "packet_type": str(packet.get("packet_type", "unknown")),
        "raw_fields": dict(packet),
        "source": str(packet.get("source", "noscore")),
    }
    player = packet.get("player")
    if isinstance(player, Mapping):
        result["player"] = {key: player[key] for key in KNOWN_PLAYER_FIELDS if key in player}
    entities = packet.get("entities")
    if isinstance(entities, list):
        result["entities"] = [dict(entity) for entity in entities if isinstance(entity, Mapping)]
    if "map_id" in packet:
        result["map_id"] = packet["map_id"]
    return result
