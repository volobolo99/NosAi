# Block A progress — Runtime + Perception + World Model

## Architecture decision

The optimal implementation order is:

1. canonical WorldState;
2. observation runtime pipeline;
3. temporal entity tracking;
4. confidence-aware HUD/OCR normalization;
5. minimap-to-world coordinate calibration;
6. end-to-end deterministic tests;
7. full CI validation;
8. real Windows/NosTale observation-only validation.

This ordering makes every later subsystem consume one canonical temporal world representation instead of maintaining parallel state.

## Completed

- Hardened WorldState/EntityState contracts.
- Implemented deterministic WorldModel transitions.
- Added ObservationMapper and ObservationPipeline.
- Added stable temporal entity tracking with short-occlusion retention and expiry.
- Added confidence-gated HUD/OCR state extraction and provenance.
- Added minimap-to-world coordinate mapper with scale, origin, rotation and confidence.
- Added focused regression tests for all new components.

## Safety boundary

Block A remains observation-only: no input injection, client memory manipulation,
or game-action execution is introduced by these components.

## Final gate

The remaining work is integration with the repository's real HUD/OCR and minimap
producers, deterministic end-to-end coverage, full CI, then Windows real-client
observation validation. No claim of production readiness should be made before
those gates pass.
