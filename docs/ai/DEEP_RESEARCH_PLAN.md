# Deep Research + GitHub Execution Plan

## Goal

Use research to resolve high-impact technical uncertainties before implementation, then convert conclusions into small GitHub changes with measurable acceptance criteria.

## Research tracks

### R1 — Agent architecture

Compare single-agent, manager-with-specialists, and handoff architectures for NosAi. Evaluate latency, complexity, observability, failure isolation and suitability for a game loop.

**Decision gate:** select the smallest architecture that satisfies the measured requirements.

### R2 — Perception

Compare screenshot/state perception approaches and determine when remote multimodal inference is justified versus local computer vision/features.

**Decision gate:** target accuracy and latency must be measured on representative client states.

### R3 — Decision/evaluation

Define an evaluation set covering combat, navigation, recovery, invalid states and ambiguous observations. Establish deterministic pass/fail metrics before live actions are enabled.

**Decision gate:** no live AI action path without a reproducible evaluation baseline.

### R4 — Performance

Measure model-call latency, local processing cost, memory pressure and fallback frequency. Research caching, batching and model-selection strategies only after the baseline exists.

**Decision gate:** AI must fit the project's hardware/resource budget without destabilizing the runtime.

### R5 — Reliability and recovery

Research failure modes including API unavailability, timeouts, malformed outputs, stale state, contradictory tools and partial client connectivity.

**Decision gate:** every failure mode has a deterministic safe fallback and diagnostic identifier.

## GitHub workflow

1. Create one issue per research decision.
2. Attach sources and the accepted decision to the issue.
3. Implement only the selected option in a focused branch.
4. Add tests and benchmarks in the same change when practical.
5. Open a PR and require CI before merge.
6. Record the final architectural decision in `docs/ai/`.

## Research-to-code rule

Research does not justify code by itself. A change enters the runtime only when it has:

- a clear problem statement;
- evidence from authoritative sources and project measurements;
- an explicit alternative comparison;
- measurable acceptance criteria;
- a rollback/fallback path.

## Current priority order

`R1 Agent architecture -> R3 Evaluation -> R4 Performance -> R5 Reliability -> R2 Perception`

This order deliberately avoids adding expensive perception or agent complexity before the evaluation and performance gates exist.
