# Block A progress — Runtime + Perception + World Model

## Confirmed optimal sequence

1. Canonical WorldState.
2. Observation runtime pipeline.
3. Temporal entity tracking.
4. Confidence-aware HUD/OCR normalization.
5. Minimap-to-world coordinate calibration.
6. Deterministic E2E tests.
7. CI regression gate.
8. Real Windows/NosTale observation-only validation.

This ordering makes every later subsystem consume one canonical temporal world representation instead of maintaining parallel state.

## Current implementation

- WorldState and deterministic WorldModel are implemented.
- ObservationPipeline emits immutable observation events and isolated snapshots.
- EntityTracker keeps stable IDs across frames and retains short occlusions until expiry.
- HudStateExtractor applies confidence gates and provenance.
- MinimapWorldMapper supports origin, scale, rotation and calibration confidence.
- HUD values now travel through the runtime pipeline into WorldState and emitted events.
- Deterministic E2E coverage exercises multiple frames, identity continuity and HUD state.

## Validation status

The repository CI workflow is configured to run on feature branches and executes source validation, dependency checks, compileall, pytest, and an AI evaluation gate. A workflow run must be observed on the branch before claiming CI success.

The remaining real-client gate requires Windows plus the optional vision dependencies and a real NosTale window. The existing Windows perception layer is read-only and must remain observation-only.

## Safety boundary

No input injection, process-memory manipulation, or game-action execution is introduced by Block A.
