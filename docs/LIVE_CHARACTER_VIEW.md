# Live Character View

NosAi now exposes an observation-only visual pipeline for the real Windows NosTale client.

## Pipeline

`WindowsNosTaleAdapter` → `WindowsNosTalePerception` → `live_character_view` → `/api/character-view` → dashboard canvas.

The dashboard refreshes the transparent RGBA subject view every 1.5 seconds. The renderer uses the captured client frame as input and removes the surrounding playfield with an OpenCV GrabCut foreground mask. No input injection, process-memory patching, or game action is performed.

## Activity and abilities

Frame-to-frame visual change is exposed as `IDLE` or `ACTIVE` with a normalized activity score. A skill name is intentionally reported as `NOT OBSERVED` until a future client adapter can provide a trustworthy observed ability event. The system never guesses a skill name from a visual change alone.

## Endpoints

- `GET /api/perception` — live frame metadata and character-view URL.
- `GET /api/character-view` — transparent RGBA PNG with activity headers.
- `GET /api/character-state` — activity state and observed ability metadata.
- `GET /api/screenshot` — original client screenshot for debugging/vision.

## Verification

`tests/test_live_character_view.py` covers RGBA PNG generation and frame-change activity detection. The feature remains observation-only and is disabled automatically when the Windows runtime adapter or vision dependencies are unavailable.
