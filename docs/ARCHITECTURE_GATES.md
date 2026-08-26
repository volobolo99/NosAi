# NosAi Architecture Gates

These gates prevent the project from growing by accumulation of disconnected features.

## G1 — Correctness
- typed contracts
- deterministic unit tests
- validation of malformed/partial observations
- reproducible fixtures

## G2 — Safety
- observation-only default
- action validation before controller
- stale-state rejection
- explicit emergency stop
- fail-closed behavior

## G3 — Learning integrity
- versioned replay schema
- provenance for trajectories
- train/eval separation
- held-out evaluation
- checkpoint metadata

## G4 — Explainability
Every strategic decision should expose:
- selected action
- candidate actions
- score components
- confidence
- reason codes
- state timestamp/version

## G5 — Performance
Measure:
- observation latency
- decision latency
- controller latency
- memory/replay I/O
- CPU/RAM usage
- dropped/stale observations

## G6 — Regression
No new subsystem is considered complete until it has tests and does not break the previous phase.

## G7 — External dependency hygiene
- pin compatible versions where practical
- isolate optional dependencies
- document license/source
- provide graceful degradation when optional components are absent
