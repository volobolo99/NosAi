"""Local NosTale asset registry primitives.

The registry stores metadata and provenance, never proprietary binary assets.
It is intentionally format-aware enough to describe player sprite animation
chains while delegating binary parsing to Taletool/format adapters.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class AnimationFrame:
    sprite_frame_index: int
    event_timing_flag: int = 0


@dataclass(frozen=True)
class SpriteAnimation:
    animation_id: str
    frames: tuple[AnimationFrame, ...]
    looping: bool = False
    frame_ticks: int = 60


@dataclass(frozen=True)
class ResourceRemap:
    sprite_frame_index: int
    slots: tuple[int, ...]


@dataclass(frozen=True)
class AssetReference:
    asset_id: str
    family: str
    relative_path: str
    sha256: str | None = None
    source: str = "client_locale"
    metadata: dict[str, str] = field(default_factory=dict)


class AssetRegistry:
    """In-memory registry used by extraction and renderer integration tests."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.assets: dict[str, AssetReference] = {}
        self.animations: dict[str, SpriteAnimation] = {}
        self.remaps: dict[int, ResourceRemap] = {}

    def add_asset(self, asset: AssetReference) -> None:
        self.assets[asset.asset_id] = asset

    def add_animation(self, animation: SpriteAnimation) -> None:
        self.animations[animation.animation_id] = animation

    def add_remap(self, remap: ResourceRemap) -> None:
        self.remaps[remap.sprite_frame_index] = remap

    def resolve_frame_resources(self, sprite_frame_index: int) -> tuple[int, ...]:
        remap = self.remaps.get(sprite_frame_index)
        if remap is None:
            return tuple(range(8))
        return tuple(index for index in remap.slots if 0 <= index < 8)

    def animation_frame(self, animation_id: str, frame_number: int) -> AnimationFrame | None:
        animation = self.animations.get(animation_id)
        if animation is None or not animation.frames:
            return None
        if animation.looping:
            frame_number %= len(animation.frames)
        else:
            frame_number = min(frame_number, len(animation.frames) - 1)
        return animation.frames[frame_number]

    def families(self) -> tuple[str, ...]:
        return tuple(sorted({asset.family for asset in self.assets.values()}))

    def local_assets_only(self) -> tuple[AssetReference, ...]:
        return tuple(asset for asset in self.assets.values() if asset.source == "client_locale")

    def add_many(self, assets: Iterable[AssetReference]) -> None:
        for asset in assets:
            self.add_asset(asset)
