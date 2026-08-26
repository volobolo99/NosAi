"""Optional Taletool integration boundary.

NosAi does not bundle proprietary client assets or assume a particular
Taletool installation. The adapter is intentionally conservative: it only
accepts structured JSON emitted by a user-installed parser and normalizes the
metadata needed by the renderer.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from .asset_registry import AnimationFrame, AssetReference, AssetRegistry, ResourceRemap, SpriteAnimation
from .nos_format_pipeline import ParsedAssetSet


class TaletoolAdapter:
    name = "taletool"

    def __init__(self, executable: str | Path) -> None:
        self.executable = Path(executable).expanduser().resolve()

    def parse(self, root: Path) -> ParsedAssetSet:
        if not self.executable.is_file():
            raise FileNotFoundError(self.executable)
        completed = subprocess.run(
            [str(self.executable), "scan", "--data-dir", str(root), "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr[-4000:] or f"Taletool exit code {completed.returncode}")
        try:
            payload: dict[str, Any] = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise ValueError("Taletool non ha restituito JSON valido") from exc

        registry = AssetRegistry(root)
        for item in payload.get("assets", []):
            registry.add_asset(AssetReference(
                asset_id=str(item["id"]),
                family=str(item.get("family", "unknown")),
                relative_path=str(item["path"]),
                sha256=item.get("sha256"),
                source="client_locale",
                metadata={str(k): str(v) for k, v in item.get("metadata", {}).items()},
            ))
        for item in payload.get("animations", []):
            frames = tuple(AnimationFrame(int(f["sprite_frame_index"]), int(f.get("event_timing_flag", 0))) for f in item.get("frames", []))
            registry.add_animation(SpriteAnimation(str(item["id"]), frames, bool(item.get("looping", False)), int(item.get("frame_ticks", 60))))
        for item in payload.get("remaps", []):
            registry.add_remap(ResourceRemap(int(item["sprite_frame_index"]), tuple(int(v) for v in item.get("slots", []))))
        return ParsedAssetSet(source_root=root.resolve(), registry=registry, parser=self.name)
