from app.assets.animation_pipeline import build_render_frame
from app.assets.asset_registry import AnimationFrame, AssetRegistry, ResourceRemap, SpriteAnimation


def test_build_render_frame_follows_animation_and_remap() -> None:
    registry = AssetRegistry(".")
    registry.add_animation(SpriteAnimation("walk", (AnimationFrame(10), AnimationFrame(11)), frame_ticks=60))
    registry.add_remap(ResourceRemap(11, (2, 0, 1)))

    frame = build_render_frame(registry, animation_id="walk", frame_number=1)

    assert frame is not None
    assert frame.sprite_frame_index == 11
    assert frame.duration_ticks == 60
    assert tuple(layer.slot for layer in frame.layers) == (2, 0, 1)
    assert all(layer.sprite_frame_index == 11 for layer in frame.layers)


def test_unknown_animation_does_not_create_fake_render_state() -> None:
    assert build_render_frame(AssetRegistry("."), animation_id="missing", frame_number=0) is None
