# ZMSIA mock orchestration slice

This slice proves the provider-neutral Core can execute a deterministic observe -> state -> decision -> action cycle without the live client, external tools, or an OpenAI dependency.

## Safety boundary

`ZMSIAOrchestrator.run_once()` deliberately stops before action execution. A future executor must sit behind validation and the safety gate.

## Next integration order

1. Validate the existing contracts and test gate.
2. Add M1/M2 adapters at the contract boundary.
3. Add action validation and safety policy.
4. Add evaluation/telemetry hooks.
5. Add local and OpenAI providers behind `DecisionProvider`.
6. Add the client adapter only after dry-run and replay tests pass.
