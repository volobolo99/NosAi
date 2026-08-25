# NosAi — Complete Phase Structure

Target architecture for the full roadmap. Directories are activated only when their phase starts; no empty runtime placeholders are required.

## Phase 0 — Data Intelligence Foundation
`app/static_data/`, `app/data/`, `tests/static_data/`

Providers, gateway, normalization, validation, provenance, caching, synchronization, snapshots and indexes.

## Phase 1 — Technical Audit
`app/diagnostics/`, `tests/audit/`, `docs/audit/`

Dependency graph, dead-code analysis, exception paths, lifecycle, persistence, performance and regression baseline.

## Phase 2 — Architecture Consolidation
`app/core/`, `app/runtime/`, `app/interfaces/`, `tests/architecture/`

Stable contracts, dependency direction, module boundaries and migration away from duplicated legacy paths.

## Phase 3 — Real Client Adapter
`app/client/`, `app/client/transports/`, `app/client/state/`, `tests/client/`

Client discovery, connection, health, state capture, synchronization, reconnect and safe shutdown.

## Phase 4 — Safety Governor
`app/safety/`, `app/actions/`, `tests/safety/`

Action validation, confidence gates, rate limits, stale-state rejection, watchdog and emergency stop.

## Phase 5 — World Model
`app/world/`, `app/world/entities/`, `app/world/state/`, `tests/world/`

Canonical live game state, entities, map, player, resources, objectives and confidence/freshness.

## Phase 6 — Perception Engine
`app/perception/`, `app/perception/capture/`, `app/perception/detection/`, `app/perception/tracking/`, `tests/perception/`

Capture, OCR, detection, tracking, UI interpretation and temporal fusion.

## Phase 7 — Decision + Combat Engine
`app/decision/`, `app/combat/`, `app/planning/`, `tests/decision/`, `tests/combat/`

Utility scoring, prediction, replanning, target selection, skills, positioning and combat recovery.

## Phase 8 — Memory + Learning
`app/memory/`, `app/learning/`, `tests/memory/`, `tests/learning/`

Working/episodic/semantic memory, experience storage, strategy adaptation and learning boundaries.

## Phase 9 — Self-Healing
`app/recovery/`, `tests/recovery/`

Anomaly detection, diagnosis, recovery plans, validation and controlled resume.

## Phase 10 — Adaptive Performance
`app/performance/`, `app/scheduler/`, `tests/performance/`

Hardware-aware budgets, adaptive perception/inference, scheduling, resource control and performance regression.

## Phase 11 — Digital Twin
`app/simulation/`, `app/simulation/world/`, `app/simulation/scenarios/`, `tests/simulation/`

Deterministic game-state simulation, scenario generation, replay and safe AI evaluation.

## Phase 12 — Strategy Optimizer
`app/optimization/`, `tests/optimization/`

Multi-objective strategy search, reward/risk/cost optimization and strategy evaluation.

## Phase 13 — Advanced Pathfinding
`app/pathfinding/`, `app/pathfinding/maps/`, `tests/pathfinding/`

Navigation graph, dynamic obstacles, risk/cost maps and learned route quality.

## Phase 14 — Event Runtime + Observability
`app/events/`, `app/observability/`, `app/telemetry/`, `tests/runtime/`

Event-driven execution, metrics, traces, decision timelines, health dashboards and runtime diagnostics.

## Phase 15 — Release Gate 5.0
`tests/e2e/`, `tests/regression/`, `tests/fault_injection/`, `tests/long_run/`, `release/`, `docs/release/`

Complete validation pipeline, real-client preflight, long-run stability, fault injection, performance gates and release evidence.

## Cross-cutting rules

1. Dependencies flow toward stable interfaces.
2. External data requires validation, provenance and freshness checks before entering the World Model.
3. Actions pass through the Safety Governor before execution.
4. New subsystems receive appropriate unit, integration and regression coverage.
5. Avoid empty placeholder runtime modules.
6. Reuse existing benchmark and diagnostics infrastructure instead of duplicating it.
