# v4.19.1 Release Gate Hardening

The release gate no longer accepts precomputed booleans as evidence for the critical reliability checks.

## Evidence required

1. **Long run:** executes 10,000 real deterministic world-model transitions and checks an invariant on every iteration.
2. **Fault injection:** injects a real runtime exception and requires the expected exception type.
3. **Recovery:** mutates runtime state, injects a failure, restores a checkpoint and validates state integrity.
4. **Reproducibility:** executes the same deterministic runtime trace three times and compares canonical SHA-256 digests.
5. **End-to-end:** runs the actual integration decision path (`NosAiIntegration.decide`), applies the selected action to `SimpleNosTaleSandbox`, feeds the outcome back into `NosAiIntegration.learn`, and verifies deterministic replay.
6. **Tests/build/integrity:** full pytest, compileall, wheel build and artifact integrity are separate release evidence.

A release is not promoted by passing a boolean-only `full_gate` call.
