# NosAi — Offline-First Evolution Architecture V2

Date: 2026-08-27
Branch: `develop/nosai-next`
Status: **architectural baseline for the next validation cycle**

## 1. Core principle

> **Internet makes NosAi grow; Internet must never be required for NosAi to play.**

The gameplay engine is offline-first. Online services are an asynchronous research, knowledge, evaluation and engineering layer. Online results are never injected directly into production gameplay behavior.

## 2. System layers

```text
                         ONLINE WORLD
      Web / GitHub / APIs / Cloud AI / external knowledge
                              |
                       Research Gateway
                              |
                provenance + trust + deduplication
                              |
                       Evolution Lab
      +-----------------------+------------------------+
      |                       |                        |
  Error Analysis         Candidate Factory       Knowledge Intake
      |                       |                        |
      +------------- Simulation / Replay ------------+
                              |
                     Evaluation & Ensemble
                              |
                    Promotion Firewall
                              |
                  OFFLINE STAGING CORE
                              |
                 Anti-forgetting regression
                              |
                     REAL-WINDOWS GATE
                              |
                     REAL-NOSTALE GATE
                              |
                  OFFLINE CONSOLIDATION
                              |
                        OFFLINE CORE
                              |
                        GAMEPLAY
                              |
                    Experience / Reward
                              |
                    Local Event Store
                              |
                       Evolution Lab
```

## 3. Offline Core

The offline core contains the capabilities required to play:

- perception/state normalization;
- world model;
- executive controller/planner;
- decision engine;
- local model inference;
- RL policy interface;
- memory and knowledge cache;
- strategy layer;
- replay/event store;
- reward and learning signals;
- real-client runtime boundary.

The core must expose an explicit **capability matrix** with `offline_required`, `online_optional`, `degraded`, and `unavailable` states. A loss of Internet must not silently change the meaning of a PASS result.

## 4. Online Evolution Layer

Online services may provide:

- new technical knowledge;
- external code references;
- documentation;
- model candidates;
- strategy hypotheses;
- error solutions;
- benchmark data;
- AI assistance;
- repository/version information.

The Research Gateway normalizes all results and records provenance. A source is evidence, never truth.

## 5. Knowledge maturity

Every external or newly learned item has one maturity state:

`candidate -> experimental -> validated -> consolidated`

### Candidate
Observed from a source or generated from experience. It has not been trusted.

### Experimental
Used inside an isolated simulation/replay environment.

### Validated
Passes defined tests and regression requirements.

### Consolidated
Repeatedly useful, traceable to evidence, compatible with the current runtime, and accepted by the promotion gate.

No lower state may be silently treated as a higher state.

## 6. Continual learning without catastrophic forgetting

NosAi must improve without destroying previously acquired capabilities.

Every evolution run therefore keeps:

- a new-experience set;
- a fixed regression/replay set;
- a safety/constraint set;
- representative historical scenarios;
- baseline metrics;
- candidate metrics;
- delta metrics.

A candidate is rejected from consolidation when it improves new scenarios but causes an unacceptable regression on protected historical scenarios.

Avalanche is an architectural reference for streams, replay, benchmarks and continual-learning evaluation. River is a reference for lightweight streaming learning and concept-drift detection. Neither becomes a mandatory runtime dependency until an isolated benchmark proves a measurable advantage.

## 7. Concept drift

Streaming observations may detect that the environment, client behavior, strategy distribution or model inputs have changed.

A drift signal can:

1. open an evolution investigation;
2. increase observation/evaluation frequency;
3. create a replay scenario;
4. request online research when available.

A drift signal **cannot** directly rewrite the production policy.

## 8. Model / strategy registry

Every model, policy, strategy package and consolidated knowledge snapshot must have:

- stable ID;
- semantic version or immutable revision;
- parent revision;
- source commit;
- training/evolution run ID;
- data/replay snapshot ID;
- environment profile;
- metrics;
- validation status;
- provenance;
- rollback target.

A registry entry is required before promotion.

## 9. Reproducibility

An evolution run must be reconstructable from:

`source_commit + model_revision + replay_snapshot + parameters + environment_profile + evidence_ids + test_results`

DVC is a candidate for large datasets/model artifacts and reproducible pipelines when Git is no longer sufficient. It is not required for ordinary source files.

## 10. Unified observability

Use a single correlation chain:

`run_id -> agent_id -> scenario_id -> state_id -> tool_call_id -> model_call_id -> evidence_id -> test_result_id`

OpenTelemetry-compatible traces and metrics are preferred over a second proprietary telemetry format. Prompt/completion content is not recorded by default; sensitive content requires explicit opt-in and redaction.

## 11. Local inference

`NosAiLLM` remains an abstraction.

Preferred offline path:

`NosAiLLM -> local provider -> llama.cpp candidate`

Optional online path:

`NosAiLLM -> cloud provider`

Optional future high-throughput server path:

`NosAiLLM -> vLLM server`

The gameplay controller must not depend on any one provider.

## 12. Memory

Memory is divided into:

- working memory;
- episodic experience;
- semantic knowledge;
- strategy memory;
- protected regression memory;
- candidate knowledge.

Qdrant remains a candidate backend for semantic retrieval. The current NosAi memory remains authoritative until benchmark results justify migration.

## 13. Promotion Firewall

The promotion firewall is the most important safety boundary.

```text
Internet / Learning
        |
     candidate
        |
    simulation
        |
   evaluation
        |
 anti-forgetting
        |
 offline staging
        |
 real Windows
        |
 real NosTale
        |
 human confirmation
        |
 consolidated offline core
```

Simulation PASS never equals production PASS.

## 14. Failure handling

If an online provider is unavailable:

- gameplay continues using the offline capability set;
- the evolution run records `ONLINE_UNAVAILABLE`;
- no online-dependent capability is falsely reported as successful;
- queued research may resume later.

If a candidate fails simulation:

- it remains evidence-linked;
- it is not silently deleted;
- its failure can be used to improve future candidate ranking.

If a candidate passes simulation but fails real Windows/NosTale validation:

- it is rejected from consolidation;
- the exact real-world evidence is retained;
- the candidate may return to the Evolution Lab as a new experimental case.

## 15. Dashboard requirements

The Evolution dashboard should expose:

- current evolution run;
- online/offline status;
- knowledge counts by maturity;
- simulation progress;
- candidate count;
- ensemble/composite candidates;
- protected-regression score;
- drift signals;
- model/strategy revision;
- promotion-gate state;
- provenance/evidence IDs;
- rollback target;
- detailed annotations.

The dashboard reports facts and test results. It does not silently decide or hide remediation details.

## 16. Definition of success

The architecture is successful when NosAi can:

1. play without Internet;
2. collect real experience;
3. detect useful learning opportunities;
4. research online when Internet is available;
5. create multiple candidates;
6. combine compatible candidates when evidence supports it;
7. simulate candidates in isolation;
8. detect regressions/forgetting;
9. validate on the real Windows runtime;
10. validate against the real NosTale client;
11. consolidate only validated improvements;
12. roll back to the previous known-good state;
13. repeat the cycle indefinitely.
