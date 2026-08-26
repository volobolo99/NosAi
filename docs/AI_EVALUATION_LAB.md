# NosAi AI Evaluation Lab

## Purpose

The AI Evaluation Lab is an offline/optional experimentation layer for NosAi. It is not a runtime dependency and must never be required for the local game runtime, safety gate, CI, or action transport.

## Architecture

```text
Scenario / replay
      |
      v
World-state fixture
      |
      +----> Candidate model / prompt A
      +----> Candidate model / prompt B
      +----> NosAi baseline
      |
      v
Normalized decision
      |
      v
Evaluator
  |    |    |
  |    |    +-- safety violations
  |    +------- expected decision / constraints
  +------------ latency / confidence / outcome
      |
      v
Evaluation evidence
      |
      +----> dashboard
      +----> regression dataset
      +----> CI gate (only for checked-in deterministic fixtures)
```

## Rules

1. The lab may call an external model provider, including AI Studio during human experimentation, but NosAi must remain functional without it.
2. Secrets and provider credentials are server-side only; never store them in fixtures, HTML, logs, or committed datasets.
3. Evaluation inputs are sanitized game-state fixtures or recorded observations, not live action commands.
4. The evaluator compares decisions; it does not execute game actions.
5. A model result cannot bypass the Planner or Safety Gate.
6. Every result carries scenario id, model/prompt identifier, timestamp, evidence version, and evaluation status.
7. Deterministic fixtures used in CI must not depend on network availability or an external model.

## Scenario schema

Required fields:

- `scenario_id`
- `world_state`
- `available_actions`
- `constraints`
- `expected_outcome` or expected constraints
- `source`
- `schema_version`

Optional fields:

- `replay_id`
- `tags`
- `difficulty`
- `notes`

## Result schema

Each evaluation result should contain:

- `scenario_id`
- `candidate_id`
- `decision`
- `confidence`
- `status`: `PASS`, `FAIL`, or `NOT_RUN`
- `safety_status`
- `latency_ms`
- `reason_codes`
- `evidence_version`

## Metrics

Primary metrics:

- decision accuracy against expected constraints;
- safety violation rate;
- invalid-action rate;
- goal completion rate;
- confidence calibration;
- p50/p95 decision latency;
- regression rate against baseline.

Secondary metrics are only added when they support a concrete engineering decision.

## Dashboard integration

The dashboard should expose a read-only AI Lab view containing:

- scenario counts;
- candidate comparison;
- pass/fail/not-run totals;
- accuracy and safety trends;
- latency distribution;
- baseline delta;
- evidence provenance.

Live runtime controls remain outside the lab view.

## CI integration

CI should run only deterministic, local evaluation fixtures. External-model evaluations are informative and must be marked `NOT_RUN` when credentials/network access are unavailable. They must not silently become `PASS`.

Recommended pipeline:

```text
fixtures -> evaluator -> JUnit/JSON evidence -> Test Center -> artifact
```

## Initial implementation phases

1. Add scenario/result schemas and validation.
2. Add deterministic evaluator using fixtures and the current NosAi baseline.
3. Add dashboard read-only endpoint and AI Lab page.
4. Add replay comparison and regression fixtures.
5. Add optional external-provider adapter for human experiments.
6. Add CI evidence and trend reporting.

## Definition of Done

The AI Evaluation Lab is complete for the first milestone when deterministic scenarios can be evaluated offline, results are provenance-tagged, failures are visible in Test Center, and no external provider is required to start or operate NosAi.
