"""Conservative NosCore packet mapping boundary.

Only fields verified from published NosCore.Packets schemas are promoted into
canonical observations. Unknown fields remain in ``raw_fields`` so real
captures can be reprocessed when a schema is verified.
"""
from __future__ import annotations

from typing import Any, Mapping

KNOWN_PLAYER_FIELDS = frozenset({
    "entity_id", "x", "y", "hp", "max_hp", "mp", "max_mp", "direction", "target_id",
})

# Verified from the published NewIn1Packet schema. HP/MP are percentages.
IN1_FIELDS = {
    1: "name",
    3: "entity_id",
    4: "x",
    5: "y",
    6: "direction",
    13: "hp",
    14: "mp",
}


def normalize_packet(packet: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "packet_type": str(packet.get("packet_type", "unknown")),
        "raw_fields": dict(packet),
        "source": str(packet.get("source", "noscore")),
    }

    if result["packet_type"] == "in" and isinstance(packet.get("fields"), (list, tuple)):
        fields = packet["fields"]
        entity: dict[str, Any] = {
            name: fields[index] for index, name in IN1_FIELDS.items() if index < len(fields)
        }
        if entity:
            result["entity"] = entity
            result["player"] = {key: entity[key] for key in KNOWN_PLAYER_FIELDS if key in entity}
            result["entities"] = [{
                "entity_id": str(entity["entity_id"]),
                "kind": "unknown_visual",
                "x": entity.get("x"),
                "y": entity.get("y"),
                "hp": entity.get("hp"),
                "mp": entity.get("mp"),
                "name": entity.get("name"),
                "source": "noscore.in1",
            }]
        return result

    player = packet.get("player")
    if isinstance(player, Mapping):
        result["player"] = {key: player[key] for key in KNOWN_PLAYER_FIELDS if key in player}
    entities = packet.get("entities")
    if isinstance(entities, list):
        result["entities"] = [dict(entity) for entity in entities if isinstance(entity, Mapping)]
    if "map_id" in packet:
        result["map_id"] = packet["map_id"]
    return result
