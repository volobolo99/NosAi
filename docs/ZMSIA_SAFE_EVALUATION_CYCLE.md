# ZMSIA Safe Evaluation Cycle

The dry-run control loop now runs through every pre-execution gate:

```text
Observation -> State -> Plan -> Decision -> Validation -> Safety -> Evaluation -> Telemetry -> (no executor)
```

The deterministic baseline accepts only the explicit `noop` action. Any other action is denied and recorded in telemetry. No executor or live client is reachable from this path.

This is the required baseline before introducing a Local AI provider or OpenAI provider.
