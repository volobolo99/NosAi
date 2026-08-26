"""Format-neutral animation pipeline for the NosTale 2.5D renderer.

Binary parsing is intentionally kept behind adapters. The pipeline consumes
normalized animation/frame/remap records from Taletool or a future native
parser and produces deterministic render commands.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .asset_registry import AssetRegistry, SpriteAnimation


@dataclass(frozen=True)
class RenderLayer:
    slot: int
    asset_id: str
    sprite_frame_index: int


@dataclass(frozen=True)
class RenderFrame:
    animation_id: str
    frame_number: int
    sprite_frame_index: int
    layers: tuple[RenderLayer, ...]
    duration_ticks: int


def build_render_frame(
    registry: AssetRegistry,
    *,
    animation_id: str,
    frame_number: int,
    layers: Iterable[RenderLayer] = (),
) -> RenderFrame | None:
    animation: SpriteAnimation | None = registry.animations.get(animation_id)
    if animation is None:
        return None
    source_frame = registry.animation_frame(animation_id, frame_number)
    if source_frame is None:
        return None

    resolved_layers = tuple(layers)
    if not resolved_layers:
        slots = registry.resolve_frame_resources(source_frame.sprite_frame_index)
        resolved_layers = tuple(
            RenderLayer(slot=slot, asset_id=f"slot-{slot}", sprite_frame_index=source_frame.sprite_frame_index)
            for slot in slots
        )

    return RenderFrame(
        animation_id=animation_id,
        frame_number=frame_number,
        sprite_frame_index=source_frame.sprite_frame_index,
        layers=resolved_layers,
        duration_ticks=animation.frame_ticks,
    )
