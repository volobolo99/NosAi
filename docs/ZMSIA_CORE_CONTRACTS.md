# ZMSIA Core Contracts

## Purpose

This document defines the first stable integration boundary for ZMSIA. It is
provider-neutral and intentionally does not import OpenAI, a local model, or a
NosTale client implementation.

## Canonical control flow

```text
Observation
    -> State
    -> Plan
    -> DecisionProvider
    -> Decision
    -> Validation
    -> SafetyDecision
    -> Action
    -> ToolRequest
    -> ToolResult / ActionResult
    -> Observation
    -> EvaluationResult
    -> Memory / ErrorEvent
```

## Contracts

- `Observation`: evidence from perception adapters.
- `State`: normalized world representation.
- `Plan`: goal-oriented proposed sequence.
- `Decision`: provider-neutral proposed action.
- `SafetyDecision`: mandatory policy gate before execution.
- `Action`: validated executable intent.
- `ToolRequest` / `ToolResult`: capability gateway boundary.
- `ActionResult`: deterministic executor outcome.
- `EvaluationResult`: evidence for acceptance/rejection and regression checks.
- `ErrorEvent`: structured diagnostic evidence suitable for memory.

## Provider rule

The Core depends only on the `DecisionProvider` protocol. Implementations may
include local inference, OpenAI, deterministic mocks, or future providers.
Changing the provider must not require changes to Core contracts.

## Safety rule

A `Decision` is not an executable action. It must pass validation and the
Safety Gate before an `Action` can reach the Tool Gateway or client adapter.

## Compatibility rule

Existing modules such as M1/M2 and future M3-M15 integrations should use
adapters at the boundary. Existing domain types are not replaced in one shot.
Migration is incremental and must preserve current behavior until parity and
regression gates pass.

## Schema evolution

Every public contract carries `schema_version`. Breaking changes require a
new version and an explicit adapter/migration rather than silently changing
field semantics.

## Test policy

The mock provider is deterministic and side-effect free. It is the required
baseline for Core tests before enabling external model providers.
