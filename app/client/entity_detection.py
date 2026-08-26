"""Observation-only visual entity detection primitives for NosTale.

Detectors are confidence-scored and template/config driven. Public reference
candidates are explicitly weak-reference data and must not be promoted to
production entity templates without local ground truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import json


@dataclass(frozen=True)
class Detection:
    kind: str
    x: int
    y: int
    width: int
    height: int
    confidence: float
    source: str = "vision"
    observation_only: bool = True


@dataclass(frozen=True)
class Roi:
    name: str
    x: float
    y: float
    width: float
    height: float


def _crop(image, roi: Roi):
    h, w = image.shape[:2]
    x = max(0, min(w, int(w * roi.x)))
    y = max(0, min(h, int(h * roi.y)))
    rw = max(1, min(w - x, int(w * roi.width)))
    rh = max(1, min(h - y, int(h * roi.height)))
    return image[y : y + rh, x : x + rw], x, y


def load_verified_templates(
    manifest: str | Path, minimum_confidence: float = 0.78
) -> dict[str, list[Path]]:
    """Load only verified/local templates from a manifest.

    Entries marked ``candidate_only`` or ``weak_reference`` are intentionally
    ignored. This makes the public dataset useful for bootstrapping while
    preventing unverified screenshots from becoming entity ground truth.
    """
    data = json.loads(Path(manifest).read_text(encoding="utf-8"))
    out: dict[str, list[Path]] = {}
    for item in data.get("items", []):
        if item.get("status") not in {"verified", "production"}:
            continue
        if float(item.get("confidence", 0.0)) < minimum_confidence:
            continue
        kind = str(item.get("kind", ""))
        path = Path(item["path"])
        if kind and path.exists():
            out.setdefault(kind, []).append(path)
    return out


class VisualEntityDetector:
    """Detect player/NPC/mob candidates with optional OpenCV templates."""

    def __init__(
        self,
        templates: dict[str, str | Path | list[str | Path]] | None = None,
        threshold: float = 0.78,
        scales: tuple[float, ...] = (1.0,),
    ):
        self.templates: dict[str, list[Path]] = {}
        for kind, value in (templates or {}).items():
            values = value if isinstance(value, (list, tuple)) else [value]
            self.templates[kind] = [Path(v) for v in values]
        self.threshold = threshold
        self.scales = scales

    @classmethod
    def from_manifest(cls, manifest: str | Path, threshold: float = 0.78):
        templates = load_verified_templates(manifest, minimum_confidence=threshold)
        return cls(templates, threshold=threshold)

    def detect_templates(self, image) -> tuple[Detection, ...]:
        try:
            import cv2
        except ImportError as exc:
            raise RuntimeError(
                "vision requires the optional 'vision' dependencies"
            ) from exc
        out = []
        for kind, paths in self.templates.items():
            for path in paths:
                if not path.exists():
                    continue
                template = cv2.imread(str(path), cv2.IMREAD_COLOR)
                if template is None:
                    continue
                for scale in self.scales:
                    if scale <= 0:
                        continue
                    th, tw = template.shape[:2]
                    if scale != 1.0:
                        tw = max(2, int(tw * scale))
                        th = max(2, int(th * scale))
                        interpolation = cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR
                        scaled = cv2.resize(template, (tw, th), interpolation=interpolation)
                    else:
                        scaled = template
                    if scaled.shape[0] > image.shape[0] or scaled.shape[1] > image.shape[1]:
                        continue
                    result = cv2.matchTemplate(image, scaled, cv2.TM_CCOEFF_NORMED)
                    _, score, _, loc = cv2.minMaxLoc(result)
                    if score >= self.threshold:
                        out.append(
                            Detection(
                                kind,
                                loc[0],
                                loc[1],
                                scaled.shape[1],
                                scaled.shape[0],
                                float(score),
                                source="verified_template",
                            )
                        )
        return tuple(out)

    def detect(self, image, rois: Iterable[Roi] = ()) -> tuple[Detection, ...]:
        detections = list(self.detect_templates(image))
        for roi in rois:
            crop, x, y = _crop(image, roi)
            if crop.size:
                detections.append(
                    Detection(
                        f"roi:{roi.name}",
                        x,
                        y,
                        crop.shape[1],
                        crop.shape[0],
                        1.0,
                        source="roi",
                    )
                )
        return tuple(detections)


def default_rois() -> tuple[Roi, ...]:
    return (
        Roi("world", 0.05, 0.08, 0.90, 0.82),
        Roi("minimap", 0.78, 0.02, 0.21, 0.25),
        Roi("hud", 0.0, 0.78, 1.0, 0.22),
    )
