"""Transparent 2.5D avatar compositor primitives.

This module intentionally works with already-decoded sprite frames. It does
not invent artwork: the decoder supplies the original client pixels and the
animation pipeline supplies the exact frame/layer order.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence

from .animation_pipeline import RenderFrame


@dataclass(frozen=True)
class SpriteLayer:
    slot: int
    rgba: bytes
    width: int
    height: int
    offset_x: int = 0
    offset_y: int = 0


class SpriteDecoder(Protocol):
    def decode(self, asset_id: str, sprite_frame_index: int) -> SpriteLayer | None: ...


@dataclass(frozen=True)
class ComposedAvatar:
    width: int
    height: int
    layers: tuple[SpriteLayer, ...]
    transparent: bool = True


def compose(frame: RenderFrame, decoder: SpriteDecoder) -> ComposedAvatar:
    layers: list[SpriteLayer] = []
    for command in frame.layers:
        decoded = decoder.decode(command.asset_id, command.sprite_frame_index)
        if decoded is not None:
            layers.append(decoded)
    width = max((layer.width + abs(layer.offset_x) for layer in layers), default=0)
    height = max((layer.height + abs(layer.offset_y) for layer in layers), default=0)
    return ComposedAvatar(width=width, height=height, layers=tuple(layers))
