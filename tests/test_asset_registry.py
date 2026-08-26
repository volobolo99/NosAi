from app.assets.asset_registry import (
    AnimationFrame,
    AssetReference,
    AssetRegistry,
    ResourceRemap,
    SpriteAnimation,
)


def test_registry_keeps_local_asset_provenance() -> None:
    registry = AssetRegistry(".")
    registry.add_asset(AssetReference("player-1", "player_sprites", "NSppData01.NOS"))
    assert registry.local_assets_only()[0].source == "client_locale"
    assert registry.families() == ("player_sprites",)


def test_animation_uses_client_frame_timing_and_looping() -> None:
    registry = AssetRegistry(".")
    registry.add_animation(
        SpriteAnimation(
            "walk",
            (AnimationFrame(0), AnimationFrame(1, 1)),
            looping=True,
            frame_ticks=60,
        )
    )
    assert registry.animation_frame("walk", 2).sprite_frame_index == 0
    assert registry.animation_frame("walk", 1).event_timing_flag == 1


def test_resource_remap_resolves_eight_slots_and_skips_invalid_values() -> None:
    registry = AssetRegistry(".")
    registry.add_remap(ResourceRemap(3, (7, 6, 5, 4, 3, 2, 1, 0)))
    assert registry.resolve_frame_resources(3) == (7, 6, 5, 4, 3, 2, 1, 0)
    assert registry.resolve_frame_resources(99) == tuple(range(8))

    registry.add_remap(ResourceRemap(4, (0, 1, 9, 2, 8, 3, 4, 5)))
    assert registry.resolve_frame_resources(4) == (0, 1, 2, 3, 4, 5)
