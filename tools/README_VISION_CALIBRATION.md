# NosAi vision calibration

Use 3–5 real NosTale gameplay screenshots captured on the target Windows PC.
Prefer the same resolution/UI scale and include different scenes: normal map,
combat with mobs, NPC interaction area, and minimap visible.

## Automatic baseline

```bash
python tools/auto_calibrate_vision.py captures/*.png --output .nosai/vision/calibration.json
```

The command validates resolution consistency, scores the candidate World/Minimap/HUD
ROIs, and writes a reviewable profile. It never controls the game.

## Entity templates

For high-confidence Player/NPC/Mob recognition, add a small annotation file using
`tools/vision_calibration_schema.json`. Coordinates are pixel coordinates in the
original screenshot. The annotation step is intentional: semantic identity cannot
be safely inferred from arbitrary pixels without ground truth.

Recommended dataset: 3–5 screenshots, at least 2 examples each of player/NPC/mob,
plus one clean minimap. Avoid UI overlays and motion blur where possible.

## Acceptance rules

- all calibration screenshots in a profile must share resolution;
- observation_only remains true;
- entity templates require confidence threshold >= 0.78 by default;
- no calibration artifact enables action execution;
- CI must pass the calibration regression tests before a profile is accepted.
