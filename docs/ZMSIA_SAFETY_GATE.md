# ZMSIA Safety Gate

The safety gate is placed between decision generation and any future action executor.

```text
Decision -> Validate -> SafetyPolicy -> Executor
```

The initial policy is intentionally deny-by-default. Only `noop` is permitted in dry-run mode. No client adapter, shell tool, filesystem mutation, or external side effect is reachable through this gate.

## Promotion rule

Action types must be introduced explicitly with validation, tests, safety policy coverage, and evaluation evidence before they can be enabled outside dry-run.
