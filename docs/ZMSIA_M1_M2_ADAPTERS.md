# ZMSIA M1/M2 adapter boundary

## Purpose

The adapter layer prevents the new ZMSIA Core contracts from importing legacy domain objects directly.

### M1

`m1_state_to_zmsia()` maps the existing M1 `State` into the provider-neutral ZMSIA `State`. `m1_action_to_zmsia()` maps M1 action intent into the ZMSIA `Action` contract.

The adapter preserves M1 features, scenario metadata, confidence and observation provenance.

### M2

`m2_plan_to_zmsia()` accepts a small planner-compatible surface and normalizes common plan shapes into the ZMSIA `Plan` contract. It intentionally does not import a concrete M2 implementation because the current repository does not expose a stable canonical M2 module path on `main`.

## Boundary rule

M1/M2 may evolve internally. Only the adapter needs to change when their public shapes change; Core contracts remain provider/domain neutral.

## Next gate

Before connecting any live executor, add action validation, safety policy and evaluation telemetry around the adapter/orchestrator path.
