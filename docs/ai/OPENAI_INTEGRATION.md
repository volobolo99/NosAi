# OpenAI Integration Contract

## Purpose

This document defines how OpenAI capabilities may be introduced into NosAi without coupling the core runtime to a single provider.

## Runtime contract

The core AI boundary should expose four operations:

- `decide(state, objective) -> Decision`
- `validate(decision, state) -> ValidationResult`
- `fallback(state, objective) -> Decision`
- `observe(run) -> TraceMetadata`

The first implementation may use the OpenAI Agents SDK for agentic workflows. The core domain must not import SDK-specific types outside the integration layer.

## Decision schema

A model decision must contain at least:

- `action_type`
- `target`
- `parameters`
- `confidence`
- `reason_code`
- `expires_at` or an equivalent freshness constraint

The validator is authoritative. Unknown actions, invalid parameters, stale decisions and unsafe transitions are rejected locally.

## Agent layout

Recommended first implementation:

- Orchestrator: bounded manager, only when coordination is needed.
- Combat agent: combat-specific tactical reasoning.
- Navigation agent: route/position reasoning.
- Recovery agent: diagnosis and safe recovery suggestions.

Use `agents-as-tools` when the orchestrator must retain control. Use handoffs only when a specialist should own the remainder of a workflow.

## Tool boundary

Game-facing functions should be local Python tools with strict schemas. Tools may read normalized state and propose/validate actions. A tool must not silently execute an unvalidated model-generated action.

## Observability

Enable tracing during development and evaluation. Capture:

- workflow name
- model and configuration
- latency
- tool calls
- validation result
- fallback usage
- final action outcome

Sensitive inputs/outputs must be excluded or minimized according to the project's privacy policy.

## Configuration

OpenAI integration must be opt-in. Suggested environment variables:

- `NOSAI_AI_PROVIDER=none|openai`
- `OPENAI_API_KEY=<secret>`
- `NOSAI_AI_ENABLED=0|1`
- `NOSAI_AI_TIMEOUT_MS=<integer>`
- `NOSAI_AI_MAX_CALLS_PER_MINUTE=<integer>`

Secrets must never be committed to Git.

## Rollout gates

1. Offline schema/unit tests.
2. Mock-provider integration tests.
3. OpenAI API smoke test, when credentials are supplied.
4. Recorded evaluation set.
5. Latency/resource benchmark.
6. Live-client read-only validation.
7. Only then consider controlled action execution.

## Current decision

Do not add OpenAI as a mandatory dependency to the base runtime yet. First land the provider-neutral contract, evaluation harness and configuration boundary. Add the SDK as an optional AI extra once those gates are green.
