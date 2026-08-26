from app.assets.animation_pipeline import RenderFrame, RenderLayer
from app.assets.renderer2d import SpriteLayer, compose


class FakeDecoder:
    def decode(self, asset_id: str, sprite_frame_index: int):
        return SpriteLayer(slot=int(asset_id.split("-")[-1]), rgba=b"rgba", width=32, height=48)


def test_composer_preserves_layers_and_transparency() -> None:
    frame = RenderFrame(
        animation_id="walk",
        frame_number=0,
        sprite_frame_index=4,
        layers=(RenderLayer(2, "slot-2", 4), RenderLayer(0, "slot-0", 4)),
        duration_ticks=60,
    )
    avatar = compose(frame, FakeDecoder())
    assert avatar.transparent is True
    assert avatar.width == 32
    assert avatar.height == 48
    assert [layer.slot for layer in avatar.layers] == [2, 0]
