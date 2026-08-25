# NosAi AI Architecture

## Decision

NosAi will use a hybrid decision architecture. Deterministic, latency-sensitive runtime logic remains local; model-based reasoning is invoked only for bounded decisions where it adds measurable value.

```text
Game Client Adapter
        |
        v
Normalized ClientState
        |
        v
Perception / State Builder
        |
        v
Decision Controller
   |         |          |
   |         |          +--> Recovery / Safety
   |         +-------------> Navigation / Planning
   +-----------------------> Combat / Tactics
        |
        v
Structured Decision
        |
        v
Action Validator
        |
        v
Client Adapter
```

## Boundaries

- `ClientAdapter` remains the only runtime boundary to the real game client.
- AI components consume normalized state and return structured decisions.
- AI components must never bypass action validation.
- No model call is required for every game tick.
- Deterministic guards own hard constraints, cooldowns, invalid targets, and impossible actions.
- Model output is advisory until validated by the local decision/action layer.

## OpenAI integration strategy

Use the OpenAI Agents SDK for workflows that benefit from managed turns, tools, guardrails, handoffs, sessions, and tracing. Use the Responses API directly when NosAi needs to own the loop and state handling for a short, latency-sensitive path.

The initial architecture should therefore expose an internal provider-neutral interface so OpenAI is an implementation, not a dependency of the core domain model.

## Initial specialists

1. `combat` — tactical combat decisions.
2. `navigation` — route/position planning.
3. `recovery` — recovery from uncertain or invalid runtime state.
4. `orchestrator` — optional manager for bounded multi-agent workflows.

Do not enable all specialists in the live loop initially. Activate them progressively behind configuration and benchmark gates.

## Safety and performance rules

- Never execute raw model output directly.
- Validate every proposed action locally.
- Add explicit timeouts and fallback behavior around model calls.
- Prefer cached state/features when the same decision context repeats.
- Record latency and decision outcomes for evaluation.
- Keep a deterministic fallback path for API unavailability or malformed output.
- Do not introduce an OpenAI dependency into modules that can remain offline/deterministic.

## Acceptance criteria

- Core runtime remains executable without an API key.
- Live-client pre-flight remains authoritative.
- AI integration can be disabled without changing deterministic behavior.
- Every AI decision has a schema, validator, timeout and fallback.
- AI changes are covered by unit, integration and regression tests before live activation.
