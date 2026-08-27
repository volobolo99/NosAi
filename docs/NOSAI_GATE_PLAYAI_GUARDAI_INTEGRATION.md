# NosAi Gate — PlayAi ↔ GuardAi + World State Integration

## Completed in this gate

- read-only World State → CharacterSnapshot normalization boundary;
- PlayAi proposal → GuardAi evaluation bridge;
- explicit producer/supervisor metadata;
- execution authorization remains false at the bridge;
- integration regression test.

## Architecture

```text
Live/World State
      ↓ read-only
CharacterSnapshot
      ↓
PlayAi proposes objective + candidate plans
      ↓
PlayAiGuardAiBridge
      ↓
GuardAi Progression Advisor
      ├─ simulation
      ├─ probability
      ├─ risk
      └─ policy status
      ↓
Decision Fabric
      ↓
Execution/Safety gates (separate)
```

## Remaining integration work

- map the concrete runtime adapter's world-state schema into the normalized adapter;
- feed observed facts into CharacterSnapshot with provenance/confidence;
- connect real PlayAi planner output instead of test proposals;
- connect GuardAi's final verdict to the existing Decision Fabric;
- add integration tests with live adapter fixtures;
- execute the repository CI/Test Center and promote only on green evidence.

## Non-negotiable

Neither cloud output nor a GuardAi recommendation directly executes game actions. Execution remains behind the existing safety/authorization boundary.
