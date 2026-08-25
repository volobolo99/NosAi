# NosAi Test Pilot v0.1

## Purpose

The Test Pilot is the first controlled data-collection layer for NosAi. Its job is to measure what the AI can observe, decide and validate, and to expose missing client capabilities before any live action path is enabled.

## Safety boundary

- `simulation` uses only the deterministic local adapter.
- `shadow` and `dry_run` are names reserved for the same non-executing pipeline in v0.1.
- No Test Pilot API executes a game action.
- `validate_action()` is the only action-related call and is validation-only.
- `ready_for_live_action` is permanently `False` in v0.1.

## First scenarios

- `combat_basic`: complete player/entity/target state.
- `missing_target`: valid player state with no target.
- `stale_state`: intentionally incomplete state to exercise capability diagnostics.

## Local usage

```text
python -m app.pilot.cli --scenario combat_basic --ticks 100
```

or after installing the project:

```text
nosai-pilot --scenario combat_basic --ticks 100
```

Telemetry is written as append-only JSONL. The default path is `artifacts/pilot/telemetry.jsonl`.

## Current diagnostic IDs

| ID | Component | Meaning |
| --- | --- | --- |
| P001 | perception | required state capabilities are missing |
| A001 | action | proposed action rejected by adapter validation |
| C001 | client | adapter is not connected |
| C004 | client | pilot cycle raised an unexpected runtime failure |

## Next gate

Before implementing a real NosTale adapter, v0.1 must pass the pilot tests and produce stable telemetry for simulation scenarios. The next engineering step is to add a normalized capability registry and replay/evaluation records, then connect those records to the existing M1 quality/OOD/shift pipeline.
