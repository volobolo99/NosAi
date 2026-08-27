# G3.3 — PlayAi / GuardAi / Decision Fabric

## Objective

G3.3 establishes the controlled decision boundary between intelligence and any future executor.

`PlayAi → Decision → GuardAi → GuardVerdict → DecisionFabric result`

No component in G3.3 executes an action.

## PlayAi

PlayAi is a strategy provider. It receives `WorldState` and `Goal` and returns the canonical `Decision` contract. A provider can be remote, local, deterministic, or model-backed without changing the boundary.

## GuardAi

GuardAi is an independent safety gate. The default implementation rejects:

- contract-version mismatches;
- confidence outside `[0, 1]`;
- confidence below the configured threshold;
- missing rationale;
- decisions that do not explicitly set `safety_ok`.

Rejection is fail-closed and is represented by a typed `GuardVerdict`.

## Decision Fabric

`DecisionFabric` owns coordination only. It asks PlayAi for a proposal, asks GuardAi to evaluate it, and returns an immutable `FabricResult`.

`can_execute()` intentionally returns `False` in G3.3. Execution belongs to the later adapter/runtime gates and cannot be activated by the intelligence layer.

## Validation

The G3.3 tests cover approval, low-confidence rejection, missing rationale, missing safety flag, invalid confidence, and the explicit no-execution boundary.

Real model and runtime integration remain outside this gate. This keeps G3.3 deterministic, provider-neutral, offline-testable, and safe to integrate with the existing memory/retrieval/context pipeline.
