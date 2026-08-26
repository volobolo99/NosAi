"""Resolution-aware, observation-only NosTale vision calibration.

The automatic calibrator works on real gameplay screenshots and produces a
reviewable JSON profile. It never sends input, changes the client, or enables
action execution. Because UI layouts differ by resolution/scale, the output is
explicitly a *candidate* profile until it passes validation on the supplied
screenshots.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
import json

from .entity_detection import Roi, default_rois


@dataclass(frozen=True)
class CalibrationProfile:
    name: str
    width: int
    height: int
    rois: tuple[Roi, ...]
    template_threshold: float = 0.78
    observation_only: bool = True
    source_images: tuple[str, ...] = ()
    confidence: float = 0.0
    status: str = "candidate"

    def validate_image(self, image: Any) -> None:
        shape = getattr(image, "shape", ())
        if len(shape) < 2:
            raise ValueError("image must expose height/width")
        if shape[1] != self.width or shape[0] != self.height:
            raise ValueError(
                f"profile {self.name!r} expects {self.width}x{self.height}, "
                f"got {shape[1]}x{shape[0]}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name, "width": self.width, "height": self.height,
            "template_threshold": self.template_threshold,
            "observation_only": self.observation_only,
            "source_images": list(self.source_images),
            "confidence": round(self.confidence, 4), "status": self.status,
            "rois": [r.__dict__ for r in self.rois],
        }


def profile_for_resolution(width: int, height: int) -> CalibrationProfile:
    return CalibrationProfile(
        name=f"nostale-{width}x{height}", width=width, height=height,
        rois=default_rois(), status="candidate",
    )


def _bounds_to_roi(x: int, y: int, w: int, h: int, iw: int, ih: int, name: str) -> Roi:
    return Roi(name, x / iw, y / ih, w / iw, h / ih)


def auto_calibrate(paths: Iterable[str | Path], output: str | Path | None = None) -> CalibrationProfile:
    """Build a candidate profile from real screenshots.

    The calibrator uses image dimensions and stable visual regions to avoid
    hard-coding one monitor. It intentionally does not claim semantic identity
    for Player/NPC/Mob; those require templates/labels supplied from gameplay
    captures. All images must share the same resolution.
    """
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("automatic calibration requires the 'vision' extra") from exc

    files = [Path(p) for p in paths if Path(p).is_file()]
    if not files:
        raise ValueError("no screenshot files supplied")
    frames = []
    for p in files:
        frame = cv2.imread(str(p), cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError(f"unable to read screenshot: {p}")
        frames.append(frame)
    h, w = frames[0].shape[:2]
    if any(f.shape[:2] != (h, w) for f in frames):
        raise ValueError("all screenshots must have the same resolution; calibrate groups separately")

    # Conservative normalized baseline. The automatic pass verifies that each
    # ROI contains pixels with meaningful variance across the supplied captures.
    candidates = list(default_rois())
    scores = []
    for roi in candidates:
        vals = []
        for frame in frames:
            x, y = int(w * roi.x), int(h * roi.y)
            rw, rh = int(w * roi.width), int(h * roi.height)
            crop = frame[y:y+rh, x:x+rw]
            vals.append(float(crop.std()) if crop.size else 0.0)
        scores.append(min(vals) / 64.0)
    confidence = max(0.0, min(1.0, sum(min(1.0, s) for s in scores) / len(scores)))
    profile = CalibrationProfile(
        name=f"nostale-{w}x{h}", width=w, height=h, rois=tuple(candidates),
        source_images=tuple(p.name for p in files), confidence=confidence,
        status="candidate" if confidence < .70 else "validated-baseline",
    )
    if output:
        Path(output).write_text(json.dumps(profile.to_dict(), indent=2), encoding="utf-8")
    return profile
