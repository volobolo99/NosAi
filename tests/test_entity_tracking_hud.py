from app.world_model import EntityState, EntityTracker, HudStateExtractor, HudValue, TrackingConfig, WorldState


def test_entity_tracker_keeps_stable_id_for_nearby_detection():
    previous = WorldState(
        tick=1,
        entities={
            "mob:1": EntityState("mob:1", "mob", {"x": 100, "y": 100}, 0.9, "vision", 1)
        },
    )
    tracker = EntityTracker(TrackingConfig(max_distance=30))
    detections = [EntityState("temporary", "mob", {"x": 108, "y": 106}, 0.95, "vision", 2)]

    tracked = tracker.track(previous, detections)

    assert tracked[0].entity_id == "mob:1"


def test_entity_tracker_creates_new_id_when_detection_is_far_away():
    previous = WorldState(
        entities={"mob:1": EntityState("mob:1", "mob", {"x": 0, "y": 0}, 0.9)}
    )
    tracker = EntityTracker(TrackingConfig(max_distance=10))
    tracked = tracker.track(previous, [EntityState("x", "mob", {"x": 100, "y": 100}, 0.8)])

    assert tracked[0].entity_id != "mob:1"


def test_hud_extractor_ignores_low_confidence_values_and_normalizes_aliases():
    extractor = HudStateExtractor()
    result = extractor.extract(
        {
            "health": HudValue("1,234", 0.95),
            "mana": HudValue("900", 0.40),
            "lv": HudValue("99", 0.91),
        }
    )

    assert result["hp"] == 1234
    assert result["level"] == 99
    assert "mp" not in result
    assert result["hud_confidence"]["hp"] == 0.95
