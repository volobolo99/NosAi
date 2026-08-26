# ZMSIA Target Architecture

## Status

Proposed architecture for the evolution of NosAi into the ZMSIA runtime. This document is the architectural target; existing modules are migrated incrementally and must remain backward-compatible until their replacement is proven.

## Current baseline

The repository is source-first, with runtime code under `app/` and tests under `tests/`. The current release is 4.19.2. Live-client integration is intentionally observation-only and requires an explicit `ClientAdapter`; the real Windows NosTale adapter does not perform game actions. The repository already has AI evaluation primitives, benchmarking, diagnostics, a goal planner, and a learning loop.

## Target layers

```text
+--------------------------------------------------------------+
|                         ZMSIA CONTROL                        |
|        lifecycle | policy | configuration | safe mode       |
+-------------------------------+------------------------------+
                                |
                                v
+--------------------------------------------------------------+
|                         ORCHESTRATOR                         |
| task routing | agent coordination | timeouts | state       |
+-------------------------------+------------------------------+
                                |
        +-----------------------+-----------------------+
        |                       |                       |
        v                       v                       v
+---------------+       +---------------+       +---------------+
|  PERCEPTION   |       |   REASONING   |       |    MEMORY     |
| capture       |       | planner       |       | working       |
| vision        |       | decision      |       | episodic      |
| OCR           |       | analysis      |       | semantic      |
| state parse   |       | fallback      |       | errors        |
+-------+-------+       +-------+-------+       | solutions     |
        |                       |               +-------+-------+
        +-----------------------+-----------------------+
                                |
                                v
+--------------------------------------------------------------+
|                         TOOL GATEWAY                         |
| filesystem | process | browser | test | git | client tools  |
+-------------------------------+------------------------------+
                                |
                                v
+--------------------------------------------------------------+
|                         SAFETY GATE                          |
| permissions | validation | rate limits | timeout | stop     |
+-------------------------------+------------------------------+
                                |
                                v
+--------------------------------------------------------------+
|                     CLIENT / ENVIRONMENT                     |
| observation first; action transport is separately gated     |
+--------------------------------------------------------------+

Cross-cutting: diagnostics, logging, telemetry, evaluation, benchmarks.
```

## Architectural rules

1. **Observation before action.** No action transport is enabled merely because perception works.
2. **Provider-neutral reasoning.** Local models and OpenAI-backed reasoning must implement the same internal decision contract.
3. **No provider in the core domain.** OpenAI SDK details stay behind an adapter/provider boundary.
4. **Deterministic safety.** Safety checks are code-enforced and cannot be overridden by an LLM.
5. **Every action is validated before execution.** Invalid, stale, ambiguous, or low-confidence decisions fall back safely.
6. **Evaluation is offline-first.** AI changes are evaluated against deterministic/mock cases before any live-client integration.
7. **Memory is evidence, not authority.** Learned solutions are candidates; they become trusted only after evaluation.
8. **Small migrations.** Existing `m1`-`m15` modules remain usable while their responsibilities are mapped to stable capabilities.
9. **Single source of truth.** Runtime configuration belongs in the existing project configuration; visual documents never become executable configuration.
10. **No silent self-modification.** ZMSIA may propose code changes, but promotion requires tests, regression checks, and an explicit release gate.

## Capability mapping from the current codebase

| Current capability | Target layer | Migration intent |
|---|---|---|
| `app/client/*` | Client boundary | Keep; formalize observation/action contracts |
| `app/ai/evaluation.py` | Evaluation | Keep and extend with provider/model metadata |
| `app/benchmark/*` | Evaluation/Telemetry | Keep; become standard benchmark harness |
| `app/diagnostics/*` | Diagnostics/Control | Keep; expose structured health model |
| `app/goal_planner/*` | Reasoning/Planning | Keep; make planner provider-independent |
| `app/learning_loop/*` | Learning/Memory | Keep; isolate learning from live execution |
| `app/m1`-`app/m15` | Capability modules | Map each module to a stable contract before refactoring |
| `app/memory_v2/*` | Memory | Keep; define typed memory interfaces above storage |

## Canonical decision pipeline

```text
Observation -> State -> Goal -> Plan -> Candidate Decision
           -> Validation -> Safety Gate -> Execution
           -> Observation -> Evaluation -> Memory
```

A decision must carry at least:

- `decision_id`
- `timestamp`
- `goal_id`
- `source_provider`
- `model_id` (if applicable)
- `action_type`
- `parameters`
- `confidence`
- `reason/reference`
- `validation_status`
- `safety_status`
- `expires_at`

## Provider strategy

Use an internal provider interface:

```text
DecisionProvider
  |- LocalProvider
  |- OpenAIProvider
  `- MockProvider
```

`MockProvider` is mandatory for tests. `LocalProvider` is preferred for latency-sensitive, repetitive perception/decision work. `OpenAIProvider` is reserved for tasks where stronger reasoning, coding, analysis, or tool orchestration provides measurable value.

## Self-improvement boundary

```text
Failure -> Diagnose -> Search Memory -> Research -> Propose
        -> Sandbox -> Test -> Benchmark -> Regression Gate
        -> Accept candidate -> Record evidence
```

A failed experiment must never directly modify the production runtime.

## Definition of done for an architectural migration

A migrated component is complete only when:

- its interface is documented;
- unit tests exist;
- integration behavior is covered;
- failure behavior is explicit;
- metrics are emitted where relevant;
- the old path is either removed with evidence or retained as a compatibility path;
- the complete regression suite passes;
- benchmark impact is measured when performance-sensitive.
