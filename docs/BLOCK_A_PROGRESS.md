# Block A progress — Entity Tracking + HUD/OCR

## Completed in this increment

- Added temporal `EntityTracker` with configurable distance association.
- Added stable IDs for detections across consecutive observations.
- Added missed-tick bookkeeping and active-entity retention policy.
- Added `HudValue` and confidence-aware `HudStateExtractor`.
- Normalized common HUD aliases (`health/hp`, `mana/mp`, `lv/level`, `gold`).
- Added numeric normalization for OCR values and provenance/confidence retention.
- Integrated tracker and HUD extractor into `ObservationMapper`.
- Added regression tests for stable IDs, far-away detections and HUD confidence gates.

## Design constraint

All components remain observation-only. They consume detections/OCR values and
produce structured state; they do not send input, manipulate client memory, or
execute game actions.

## Next engineering gate

The next implementation step is to make the temporal tracker consume/retain
unmatched entities according to expiry semantics, then integrate actual HUD/OCR
producers and minimap/world-coordinate calibration into the same observation
pipeline. After that, run the full CI suite and validate the complete chain on
Windows with a real client in observation-only mode.
