# Changelog

## 4.20.0 — source-grounded NosTale strategy model

- Added an explicit `NosTaleState` model covering the state variables proposed by the strategic analysis.
- Added transparent room-objective strategy signals for kill-all, survival, target elimination, switch access and escort scenarios.
- Added explicit resistance-threshold and Dignity guard signals instead of hiding these assumptions inside learned weights.
- Added hardcore raid life-pool risk handling and reward-context enrichment.
- Added source provenance to generated reward metadata.
- Added regression tests for the new strategy boundaries.
- Added documentation distinguishing source-derived hypotheses from live-client validation.

## 4.19.2 — repository foundation

Infrastructure-only phase of the NosAi repository migration.

- Added repository-level Python configuration.
- Added ignore rules for generated artifacts and local environments.
- Added contribution and development guidance.
- Added CI foundation for validating the release archive.
- Preserved the runtime release archive unchanged as the migration baseline.

No runtime behavior is intentionally changed in this phase.
