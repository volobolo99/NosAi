# NosAi — OpenAI Integration Contract

## Role
OpenAI is an optional cognitive provider. It can assist PlayAi/GuardAi with strategic reasoning, difficult-state analysis, alternative generation, explanation and improvement proposals when local deterministic components are insufficient.

## Boundary
```text
NosAi Core
  ├─ State / perception
  ├─ deterministic simulation
  ├─ risk / probability
  ├─ Decision Fabric
  ├─ Test Center
  └─ Execution Safety
          |
          +---- Optional OpenAI Cognitive Provider
```

The runtime must remain operable when OpenAI is unavailable. Provider failure must produce a deterministic fallback rather than bypassing decision/safety gates.

## Structured contract
LLM-facing interfaces must use versioned structured schemas for requests and responses. Free-form model output must not directly control execution. A provider response becomes evidence/candidate reasoning that is validated by the local Decision Fabric and Safety/Control Plane.

Suggested operations:
- `strategic_analysis(state, objective)`;
- `generate_alternatives(state, objective)`;
- `review_candidate(state, candidate)`;
- `explain_decision(trace)`;
- `propose_improvement(failure_cluster)`.

## Secret handling
`OPENAI_API_KEY` must be supplied through the approved runtime secret/environment mechanism. It must never appear in Git history, source code, committed `.env` files, fixtures, logs, traces or dashboard exports.

## Cost and latency policy
OpenAI calls are subject to a compute/latency budget. Adaptive Compute decides whether a call is justified. Cache/replay may be used for deterministic evaluation, but production decisions must preserve provenance.

## Evaluation
Every OpenAI-backed component is benchmarked against a local baseline. Track:
- decision quality delta;
- GuardAi Value Added where applicable;
- latency p50/p95;
- token/cost usage;
- failure/fallback rate;
- schema-valid response rate;
- regression rate.

No provider is promoted to a mandatory dependency without evidence.

## Implementation status
This document defines the integration contract. API usage should be wired into the specific runtime module only after the repository's secret/configuration mechanism and provider adapter have been verified.
