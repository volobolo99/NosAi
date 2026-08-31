# NosAi Block A — Audit + Runtime + Perception + World Model

## Baseline audited

- Stable repository baseline: `main` / v4.19.2.
- Development target: `develop/nosai-next`.
- Feature branch: `feature/block-a-runtime-perception-world-model`.
- Python: >=3.10.
- Vision dependencies are already defined as optional (`mss`, `opencv-python`); OCR is optional via `pytesseract`.
- The live Windows adapter is observation-only and explicitly avoids input injection, memory patching and game actions.

## Findings

### Runtime/client boundary

The repository already has a concrete Windows client adapter, live observation layer, calibration, entity detection, minimap navigation and HUD/perception modules. The existing safety boundary is therefore retained: Block A must not introduce an action transport or client manipulation into perception.

### Perception

Visual capture already produces PNG frames. Entity recognition already supports confidence-scored, verified-template detection and multi-entity grouping. The next missing integration step is converting those observations into the canonical WorldState without leaking mutable objects or losing provenance/confidence.

### World Model

`app/world_model/state.py` existed but was a minimal mutable dataclass. `app/world_model/model.py` was a simulation abstraction whose `apply()` raised `NotImplementedError`. This was the main concrete gap in Block A.

## Implemented in this branch

1. Hardened `EntityState` and `WorldState` with confidence, source, observation timestamp and revision metadata.
2. Added deep isolated copies and deterministic serialization/deserialization helpers.
3. Implemented explicit data-only world transitions for simulation/replay and fail-closed behavior for unknown transitions.
4. Added `ObservationMapper` to fuse observation-only perception into `WorldState`.
5. Added regression tests for isolation, transitions, fail-closed behavior, observation fusion and tick monotonicity.

## Remaining Block A work

1. Integrate the mapper into the live observation/event pipeline.
2. Add stable entity tracking across frames so IDs do not depend only on screen coordinates.
3. Add temporal state retention/expiry for entities no longer visible.
4. Add OCR-derived character/HUD fields behind confidence thresholds.
5. Add minimap-to-world coordinate calibration and confidence metadata.
6. Add frame/event correlation IDs and provenance through the runtime event bus.
7. Add end-to-end tests using deterministic synthetic frames/observations.
8. Run the complete regression/CI suite and verify no behavior regression.
9. Validate on a real Windows NosTale client in observation-only mode before promoting the branch.

## Acceptance criteria

Block A is complete only when a real or deterministic observation can flow through:

`ClientAdapter -> Frame -> Perception -> MultiEntityObservation -> ObservationMapper -> WorldState -> Event/Telemetry`

with:

- no game action execution;
- monotonic state revision/tick;
- confidence and source preserved;
- stable serialization;
- deterministic replay of state transitions;
- regression tests green;
- real-client observation validated on Windows.
