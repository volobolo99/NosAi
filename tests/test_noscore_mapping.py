from app.integrations.noscore_mapping import normalize_packet


def test_unknown_packet_is_preserved_without_guessing():
    packet = {"packet_type": "unknown", "foo": "bar", "source": "noscore"}
    normalized = normalize_packet(packet)
    assert normalized["packet_type"] == "unknown"
    assert normalized["raw_fields"]["foo"] == "bar"
    assert "player" not in normalized


def test_known_player_fields_are_normalized():
    normalized = normalize_packet({"packet_type": "state", "player": {"x": "3", "hp": 90, "ignored": 1}})
    assert normalized["player"] == {"x": "3", "hp": 90}
