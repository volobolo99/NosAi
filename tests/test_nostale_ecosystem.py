import pytest

from app.integrations.nostale_ecosystem import (
    EntitySnapshot,
    GameStateSnapshot,
    SourceDescriptor,
    normalize_packet,
)


def test_normalize_packet_is_provider_neutral():
    source = SourceDescriptor("NosCore.Packets", "NosCoreIO/NosCore.Packets", "MIT")
    packet = normalize_packet(
        "  in_mov  ", {"x": 12}, direction="incoming", source=source
    )
    assert packet.name == "in_mov"
    assert packet.fields == {"x": 12}
    assert packet.source == source


def test_normalize_packet_rejects_invalid_direction():
    with pytest.raises(ValueError):
        normalize_packet("in_mov", direction="sideways")


def test_game_state_is_immutable_and_composable():
    entity = EntitySnapshot(entity_id=7, entity_type="player", x=10, y=20)
    state = GameStateSnapshot(tick=3, map_id=1, player_id=7, entities=(entity,))
    assert state.entities[0].entity_id == 7
    assert state.tick == 3
