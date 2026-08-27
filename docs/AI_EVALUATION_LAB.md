# NosAi AI Evaluation Lab

## Purpose

The AI Evaluation Lab is an offline/optional experimentation layer for NosAi. It is not a runtime dependency and must never be required for the local game runtime, safety gate, CI, or action transport.

## Architecture

```text
Scenario / replay
      |
World-state fixture
      |
Candidate model / prompt / RL policy
      |
Normalized decision
      |
Evaluator -> safety / constraints / latency / confidence / outcome
      |
Evaluation evidence
   |        |        |
Dashboard  Regression  CI
```

## Reusable AI research track

The lab is the controlled place to evaluate external AI/RL tooling before it enters NosAi:

- Gymnasium environment compatibility;
- PettingZoo multi-agent scenarios for PlayAi/GuardAi cooperation;
- Stable-Baselines3 baseline experiments (e.g. PPO);
- CleanRL reference implementations and algorithm cross-checks;
- RL Baselines3 Zoo configurations/benchmark comparisons;
- Agent Lightning-inspired trajectory/reward experiments;
- other game-agent repositories as architecture references;
- MALib only as a future distributed multi-agent candidate.

These are not automatically runtime dependencies. Each candidate must pass the Third-Party Component Audit.

## Rules

1. External providers/frameworks are optional; NosAi must remain functional without them.
2. Secrets and provider credentials are never stored in fixtures, HTML, logs or committed datasets.
3. Evaluation inputs are sanitized state fixtures or recorded observations, not live action commands.
4. The evaluator compares decisions; it does not execute game actions.
5. A model or RL result cannot bypass Planner or Safety Gate.
6. Results carry scenario id, candidate id, timestamp, evidence version and evaluation status.
7. Deterministic CI fixtures must not depend on network availability or an external model.
8. Framework adoption requires license, maintenance, dependency, security, API and performance review.

## Scenario schema

Required: `scenario_id`, `world_state`, `available_actions`, `constraints`, `expected_outcome` or constraints, `source`, `schema_version`.

Optional: `replay_id`, `tags`, `difficulty`, `notes`.

## Result schema

Each result should contain `scenario_id`, `candidate_id`, `decision`, `confidence`, `status` (`PASS`, `FAIL`, `NOT_RUN`), `safety_status`, `latency_ms`, `reason_codes`, and `evidence_version`.

## Metrics

Primary metrics:

- decision accuracy against expected constraints;
- safety violation rate;
- invalid-action rate;
- goal completion rate;
- confidence calibration;
- p50/p95 decision latency;
- regression rate against baseline;
- for RL experiments: reward, sample efficiency, stability and reproducibility;
- for PlayAi/GuardAi cooperation: GuardAi intervention value and unnecessary intervention rate.

## Dashboard integration

Expose a read-only AI Lab view with scenario counts, candidate comparison, pass/fail/not-run totals, accuracy/safety trends, latency, baseline delta, RL metrics and evidence provenance. Live runtime controls remain outside the lab view.

## CI integration

CI runs deterministic local fixtures. External-model/framework evaluations are informative and become `NOT_RUN` when credentials/network access are unavailable; they must not silently become `PASS`.

Recommended pipeline:

```text
fixtures -> evaluator -> JUnit/JSON evidence -> Test Center -> artifact
```

## Initial implementation phases

1. Scenario/result schemas and validation.
2. Deterministic evaluator using the current NosAi baseline.
3. Dashboard read-only AI Lab view.
4. Replay comparison and regression fixtures.
5. Gymnasium/PettingZoo environment prototypes.
6. SB3 PPO baseline and CleanRL cross-check.
7. RL Zoo benchmark/configuration comparison.
8. Optional trajectory-level experiments inspired by Agent Lightning.
9. Third-party audit and promotion decision for each adopted component.

## Definition of Done

The first research milestone is complete when deterministic scenarios run offline, results are provenance-tagged, failures are visible in Test Center, candidate frameworks are audited, and no external framework/provider is required to start or operate NosAi.
