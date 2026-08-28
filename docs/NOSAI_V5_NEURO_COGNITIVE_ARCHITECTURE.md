# NosAi v5 — Neuro-Cognitive Architecture

## Purpose

v5 integrates the existing runtime architecture with a neuro-cognitive model. The biological labels are design metaphors; software contracts remain explicit and testable.

## Cognitive areas

| Cognitive metaphor | Software boundary | Responsibility |
|---|---|---|
| Sensory cortex | `PerceptionProvider` | Convert raw signals to normalized observations |
| Thalamus | `EventGateway/EventBus` | Filter, normalize, route and correlate observations |
| Hippocampus | `EpisodicMemory + Retrieval` | Recent context and experience retrieval |
| Neocortex | `KnowledgeRepository + LearnedModels` | Consolidated semantic knowledge and learned estimators |
| Amygdala | `ValueEngine` | Salience, reward, urgency and risk |
| Prefrontal cortex | `ExecutiveController` | Goal reasoning, planning and resource arbitration |
| Basal ganglia | `ActionSelector` | Rank candidate intents and select one |
| Motor cortex | `ActionPlanner` | Translate intent into an executable action plan |
| Cerebellum | `RealtimeController` | Low-latency feedback and fine control |
| Autonomic/safety system | `SafetyController` | Independent veto, recovery and safe-stop |
| Sleep/consolidation | `ConsolidationPipeline` | Replay, evaluation and controlled knowledge updates |

## Canonical loop

```text
raw signals
  -> perception
  -> normalized Observation
  -> EventGateway
  -> WorldState update
  -> memory retrieval + ValueEngine
  -> ExecutiveController
  -> candidate plans
  -> ActionSelector
  -> ActionPlanner
  -> RealtimeController
  -> observed outcome
  -> Episode
  -> replay/consolidation
  -> validated knowledge/strategy update
```

Safety is an independent gate and may veto execution at any point.

## Memory model

### Working memory

Short-lived state needed to finish the current decision cycle: current goal, active plan, recent observations and unresolved conditions.

### Episodic memory

Structured records of state, action, outcome and reward. It is the primary source for experience-based adaptation.

### Semantic knowledge

Stable facts and validated strategy rules. Source provenance, confidence, evidence count and version are mandatory metadata.

### Learned models

Statistical/ML estimators are derived from validated episodes. They must not silently replace explicit rules or source-grounded facts.

## Consolidation policy

1. Capture episodes without modifying long-term knowledge.
2. Sanitize and deduplicate episodes.
3. Replay them in deterministic simulation when possible.
4. Measure success, reward, risk and confidence.
5. Generate candidate knowledge/strategy updates.
6. Validate candidates against regression tests and provenance.
7. Promote only validated candidates.
8. Keep prior versions for rollback and auditability.

Direct overnight fine-tuning from raw sessions is intentionally not the default.

## NosTale strategy integration

The existing `app/nostale/strategy.py` remains the source-grounded strategy adapter. v5 treats those signals as explicit hypotheses and feeds them into Value/Planning rather than hiding them inside a neural policy. Individual mechanics must be validated by observations or authoritative references before becoming hard constraints.

## Runtime boundaries

- Domain/cognition never imports a concrete client adapter.
- Perception is observation-only at the current live-client boundary.
- Action execution is intent-based and separately gated.
- Replay/simulation must be able to run without a live client.
- Every long-running operation is observable and cancellable.
- Every persisted schema is versioned.
- Every failure has a recovery or safe-stop path.

## v5 implementation sequence

1. Contracts and deterministic core.
2. WorldState projection and EventGateway integration.
3. Persistent episodic/semantic repositories.
4. Strategy candidate generation and action selection.
5. Safety controller integration.
6. Replay/consolidation pipeline.
7. Benchmarks and regression suite.
8. Perception integration after observation validation.
9. Any action transport remains separately gated and is not assumed by the cognitive core.
