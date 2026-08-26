# NosAi Vision Ground Truth

This directory is for **local NosTale gameplay captures** from the target Windows client. Public web screenshots in `data/vision/reference_sources.json` are reference material only and must not be promoted to ground truth.

## Capture set

Use 5-10 full-window screenshots at the target resolution/UI scale:

1. Player idle with minimap visible.
2. One NPC clearly visible and not overlapping the player.
3. One mob clearly visible.
4. Multiple mobs / combat scene.
5. Target selected with target HUD visible.
6. Optional: different map/scene at the same resolution.

## Annotation format

Create one JSON file per screenshot with normalized coordinates (`0..1`):

```json
{
  "image": "capture_001.png",
  "width": 1920,
  "height": 1080,
  "rois": {
    "world": [0.0, 0.0, 1.0, 0.9],
    "hud": [0.0, 0.0, 1.0, 1.0],
    "minimap": [0.82, 0.0, 0.18, 0.22]
  },
  "entities": [
    {"id":"player_001","class":"player","bbox":[0.45,0.42,0.06,0.12],"confidence":1.0},
    {"id":"mob_001","class":"mob","bbox":[0.52,0.43,0.08,0.11],"confidence":1.0},
    {"id":"npc_001","class":"npc","bbox":[0.34,0.40,0.07,0.12],"confidence":1.0}
  ]
}
```

Classes are restricted to `player`, `npc`, `mob`, and optionally `pet`/`nosmate`.

## Acceptance rules

- A screenshot with ambiguous identity is marked `uncertain` and is not used as a positive template.
- Ground truth must come from the target client, not a web image.
- Calibration remains `observation_only`.
- A template is accepted only after validation on held-out captures; the runtime threshold defaults to `0.78`.
- No annotation enables action execution.
