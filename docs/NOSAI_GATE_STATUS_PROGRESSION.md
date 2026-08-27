# NosAi — Progression Advisor Gate Status

Date: 2026-08-27

## Implemented in source

- `app/progression/models.py`: versioned CharacterSnapshot, ProgressionPlan and PlanResult.
- `app/progression/simulator.py`: seeded Monte Carlo evaluator with stable cross-process seeding, percentile timing, utility ranking and policy filtering.
- `app/progression/advisor.py`: GuardAi-side advisor, bottleneck analysis, ranking and dashboard-safe payload.
- `tests/test_progression_advisor.py`: snapshot validation, deterministic simulation, policy filtering and advisor output tests.

## Existing foundations reused

The repository already has hierarchical goal decomposition and an externalized executor boundary; these remain separate from the advisory simulator. The current goal planner supports EXP, ITEM, QUEST, PVM, PVP and UPGRADE templates and produces dependency-aware subgoals. The executor only tracks plan progress and delegates real execution to external adapters.

## Gate decision

**IMPLEMENTATION:** PASS for the new pure advisory layer.

**DASHBOARD API/UI:** INTEGRATE — endpoint wiring and main-dashboard rendering remain the next integration step.

**LIVE CLIENT:** NOT ENABLED — current repository baseline keeps the Windows client boundary observation-only.

**CI:** PENDING runtime execution of the new tests in the repository's configured CI environment. The latest commit currently has no reported commit-status checks, so this document must not claim CI-green without an actual run.

## Required next gate

1. Wire `/api/progression-advisor` into the existing FastAPI dashboard.
2. Feed it a validated CharacterSnapshot from the observation/runtime state when available.
3. Render the top three plans, probabilities, time bands, utility, confidence and policy status.
4. Add integration tests for the endpoint and dashboard payload.
5. Run the complete Test Center/CI suite.
6. Only then promote the gate to PASS.
