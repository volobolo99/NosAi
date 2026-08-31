# Windows / NosTale observation-only E2E

## Purpose

Validate the real Windows capture boundary before enabling any action/control subsystem.

## Preconditions

- Windows host.
- NosTale client open in a visible window.
- Python environment matching repository CI.
- Pillow installed for screen capture.
- Existing perception dependencies installed if visual inference is enabled.

## Procedure

1. Start NosTale normally and leave the client idle.
2. Run `python tools/windows_observation_e2e.py --frames 30 --interval 0.2`.
3. Inspect `artifacts/windows_observation/report.json`.
4. Verify that all captured records have `observation_only=true`.
5. Feed the captured frames through the existing perception adapter and inspect detections.
6. Verify temporal identity continuity, HUD confidence filtering and minimap calibration.
7. Store the report/artifacts as the Block A validation artifact.

## Acceptance criteria

- Capture succeeds on Windows.
- No input injection occurs.
- No process-memory access occurs.
- Frames are timestamped/ordered and reproducible enough for debugging.
- Player/entity detections reach `ObservationPipeline`.
- Stable IDs persist across consecutive frames when entities remain visible.
- Low-confidence HUD values are rejected.
- Minimap calibration reports explicit confidence.
- WorldState and ObservationEvent remain serializable.

## Safety boundary

This harness is intentionally read-only. It captures screen observations only and
must not be extended with keyboard/mouse injection or process-memory operations.
Those concerns belong outside Block A and require a separate design/validation gate.
