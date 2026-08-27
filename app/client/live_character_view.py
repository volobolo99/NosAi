"""Observation-only live character/ability visualizer helpers.

The module never injects input or touches game memory. It derives a transparent
subject view from the captured client frame and reports visual activity so the
dashboard can show live movement/ability activity without pretending to know a
skill name that the observation adapter did not actually observe.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CharacterView:
    png: bytes
    width: int
    height: int
    activity_score: float
    activity_state: str
    source: str = "windows_screen_capture_grabcut"
    observation_only: bool = True


def _require_vision():
    try:
        import cv2
        import numpy as np
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Live character view requires the 'vision' dependencies") from exc
    return cv2, np


def _transparent_subject(image):
    cv2, np = _require_vision()
    h, w = image.shape[:2]
    if w < 32 or h < 32:
        raise ValueError("captured frame is too small for subject extraction")

    # Keep the central playfield; NosTale HUD/chrome is normally concentrated
    # near the outer edges. GrabCut then refines the foreground boundary.
    margin_x, margin_y = max(4, int(w * 0.08)), max(4, int(h * 0.10))
    crop = image[margin_y : h - margin_y, margin_x : w - margin_x].copy()
    ch, cw = crop.shape[:2]
    mask = np.full((ch, cw), cv2.GC_PR_BGD, dtype=np.uint8)
    border = max(3, min(cw, ch) // 30)
    mask[:border, :] = cv2.GC_BGD
    mask[-border:, :] = cv2.GC_BGD
    mask[:, :border] = cv2.GC_BGD
    mask[:, -border:] = cv2.GC_BGD
    # The game subject is expected in the playfield, but leave a conservative
    # probable-foreground region rather than forcing a hard rectangle.
    y0, y1 = int(ch * 0.18), int(ch * 0.88)
    x0, x1 = int(cw * 0.18), int(cw * 0.82)
    mask[y0:y1, x0:x1] = cv2.GC_PR_FGD

    bgd = np.zeros((1, 65), np.float64)
    fgd = np.zeros((1, 65), np.float64)
    cv2.grabCut(crop, mask, None, bgd, fgd, 2, cv2.GC_INIT_WITH_MASK)
    alpha_mask = np.where(
        (mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0
    ).astype(np.uint8)

    # Remove tiny isolated islands while preserving effect-sized regions.
    kernel = np.ones((3, 3), np.uint8)
    alpha_mask = cv2.morphologyEx(alpha_mask, cv2.MORPH_OPEN, kernel, iterations=1)
    rgba = cv2.cvtColor(crop, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = alpha_mask
    ok, encoded = cv2.imencode(".png", rgba)
    if not ok:
        raise ValueError("cannot encode transparent character view")
    return encoded.tobytes(), cw, ch


def build_character_view(frame_png: bytes, previous_png: bytes | None = None) -> CharacterView:
    cv2, np = _require_vision()
    image = cv2.imdecode(np.frombuffer(frame_png, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("cannot decode captured frame")

    previous = None
    if previous_png:
        previous = cv2.imdecode(np.frombuffer(previous_png, dtype=np.uint8), cv2.IMREAD_COLOR)
    if previous is not None and previous.shape == image.shape:
        a = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        b = cv2.cvtColor(previous, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(a, b)
        score = float(np.mean(diff) / 255.0)
    else:
        score = 0.0

    png, width, height = _transparent_subject(image)
    state = "ACTIVE" if score >= 0.035 else "IDLE"
    return CharacterView(
        png=png,
        width=width,
        height=height,
        activity_score=round(score, 4),
        activity_state=state,
    )
