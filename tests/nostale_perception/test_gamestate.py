from app.nostale_perception.gamestate import GameStateBuilder, PlayerState, WorldEntity


def test_gamestate_is_json_friendly_and_preserves_unknowns():
    state = (
        GameStateBuilder(state_id="state:1", timestamp_ms=100)
        .client(pid=42, window_rect={"left": 10, "top": 20, "right": 650, "bottom": 500})
        .map("unknown")
        .player(PlayerState(hp=100, hp_max=200, confidence=0.9))
        .entities([WorldEntity(entity_id="mob:1", entity_type="mob", confidence=0.8)])
        .source("frame:1")
        .quality(stale=False, confidence=0.85)
        .build()
    )

    payload = state.to_dict()
    assert payload["player"]["hp"] == 100
    assert payload["player"]["mp"] is None
    assert payload["entities"][0]["entity_type"] == "mob"
    assert payload["source_observation_ids"] == ("frame:1",)


def test_duplicate_sources_are_deduplicated():
    state = (
        GameStateBuilder(state_id="s", timestamp_ms=1)
        .source("a", "a", "b")
        .quality(stale=False, confidence=0.0)
        .build()
    )
    assert state.source_observation_ids == ("a", "b")
