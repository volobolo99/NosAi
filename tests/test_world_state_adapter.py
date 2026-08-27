from app.progression.world_state_adapter import snapshot_from_world_state


def test_world_state_is_read_only_normalized():
    snapshot = snapshot_from_world_state({
        "snapshot_id": "s1", "timestamp": 123.0, "server": "EU",
        "character": {"level": 99, "class": "mage", "stats": {"attack": 10}, "resistances": {"fire": 20}},
        "resources": {"gold": 1000}, "inventory": {"ore": 3}, "objectives": ["raid"],
        "confidence": 0.8,
    })
    assert snapshot.level == 99
    assert snapshot.stats["attack"] == 10.0
    assert snapshot.resources["gold"] == 1000.0
    assert snapshot.validate() == ()
