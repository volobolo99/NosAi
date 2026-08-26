"""Observation-only multi-entity perception for NosTale.

Combines the calibrated world/minimap regions with verified templates for
Player/NPC/Mob detection. Public references never become production templates.
The module returns structured observations only; it cannot send input or act on
NosTale.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .entity_detection import Detection, Roi, VisualEntityDetector, _crop, default_rois


@dataclass(frozen=True)
class MinimapObservation:
    x: int
    y: int
    width: int
    height: int
    detections: tuple[Detection, ...] = ()
    confidence: float = 0.0
    source: str = "minimap"
    observation_only: bool = True


@dataclass(frozen=True)
class MultiEntityObservation:
    player: tuple[Detection, ...] = ()
    npc: tuple[Detection, ...] = ()
    mob: tuple[Detection, ...] = ()
    minimap: MinimapObservation | None = None
    world_roi: Roi | None = None
    hud_roi: Roi | None = None
    observation_only: bool = True

    @property
    def all_entities(self) -> tuple[Detection, ...]:
        return self.player + self.npc + self.mob

    def to_dict(self) -> dict[str, Any]:
        def encode(d: Detection) -> dict[str, Any]:
            return {
                "kind": d.kind,
                "x": d.x,
                "y": d.y,
                "width": d.width,
                "height": d.height,
                "confidence": round(d.confidence, 4),
                "source": d.source,
                "observation_only": d.observation_only,
            }

        mm = None
        if self.minimap is not None:
            mm = {
                "x": self.minimap.x,
                "y": self.minimap.y,
                "width": self.minimap.width,
                "height": self.minimap.height,
                "confidence": round(self.minimap.confidence, 4),
                "detections": [encode(d) for d in self.minimap.detections],
                "source": self.minimap.source,
                "observation_only": self.minimap.observation_only,
            }
        return {
            "player": [encode(d) for d in self.player],
            "npc": [encode(d) for d in self.npc],
            "mob": [encode(d) for d in self.mob],
            "minimap": mm,
            "world_roi": None if self.world_roi is None else self.world_roi.__dict__,
            "hud_roi": None if self.hud_roi is None else self.hud_roi.__dict__,
            "observation_only": self.observation_only,
        }


class MultiEntityRecognizer:
    """Run verified Player/NPC/Mob templates in world and minimap ROIs."""

    def __init__(
        self,
        detector: VisualEntityDetector,
        rois: tuple[Roi, ...] | None = None,
        threshold: float = 0.78,
    ) -> None:
        self.detector = detector
        self.threshold = threshold
        roi_map = {r.name: r for r in (rois or default_rois())}
        self.world_roi = roi_map.get("world")
        self.minimap_roi = roi_map.get("minimap")
        self.hud_roi = roi_map.get("hud")

    @classmethod
    def from_manifest(
        cls, manifest: str | Path, threshold: float = 0.78
    ) -> "MultiEntityRecognizer":
        return cls(
            VisualEntityDetector.from_manifest(manifest, threshold=threshold),
            threshold=threshold,
        )

    @staticmethod
    def _inside(image, roi: Roi):
        return _crop(image, roi)

    @staticmethod
    def _dedupe(detections: list[Detection], iou_threshold: float = 0.50) -> tuple[Detection, ...]:
        def iou(a: Detection, b: Detection) -> float:
            ax2, ay2 = a.x + a.width, a.y + a.height
            bx2, by2 = b.x + b.width, b.y + b.height
            ix1, iy1 = max(a.x, b.x), max(a.y, b.y)
            ix2, iy2 = min(ax2, bx2), min(ay2, by2)
            iw, ih = max(0, ix2 - ix1), max(0, iy2 - iy1)
            inter = iw * ih
            if not inter:
                return 0.0
            union = a.width * a.height + b.width * b.height - inter
            return inter / union if union else 0.0

        result: list[Detection] = []
        for item in sorted(detections, key=lambda d: d.confidence, reverse=True):
            if any(item.kind == old.kind and iou(item, old) >= iou_threshold for old in result):
                continue
            result.append(item)
        return tuple(result)

    def _detect_roi(self, image, roi: Roi) -> tuple[Detection, ...]:
        crop, ox, oy = self._inside(image, roi)
        if crop.size == 0:
            return ()
        local = self.detector.detect_templates(crop)
        return tuple(
            Detection(
                d.kind,
                d.x + ox,
                d.y + oy,
                d.width,
                d.height,
                d.confidence,
                source=d.source,
                observation_only=True,
            )
            for d in local
        )

    def recognize(self, image) -> MultiEntityObservation:
        world = self._detect_roi(image, self.world_roi) if self.world_roi else ()
        grouped = {"player": [], "npc": [], "mob": []}
        for d in world:
            if d.kind in grouped:
                grouped[d.kind].append(d)
        for key in grouped:
            grouped[key] = list(self._dedupe(grouped[key]))

        minimap = None
        if self.minimap_roi is not None:
            mini = self._detect_roi(image, self.minimap_roi)
            _, mx, my = self._inside(image, self.minimap_roi)
            _, mw, mh = image.shape[0], image.shape[1], image.shape[0]
            # Confidence represents the strongest verified marker; empty minimaps
            # remain valid observations with confidence 0 rather than false positives.
            confidence = max((d.confidence for d in mini), default=0.0)
            minimap = MinimapObservation(
                mx,
                my,
                max(1, int(image.shape[1] * self.minimap_roi.width)),
                max(1, int(image.shape[0] * self.minimap_roi.height)),
                tuple(self._dedupe(list(mini))),
                confidence=confidence,
            )

        return MultiEntityObservation(
            player=tuple(grouped["player"]),
            npc=tuple(grouped["npc"]),
            mob=tuple(grouped["mob"]),
            minimap=minimap,
            world_roi=self.world_roi,
            hud_roi=self.hud_roi,
            observation_only=True,
        )
