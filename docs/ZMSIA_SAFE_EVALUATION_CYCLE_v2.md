# ZMSIA Safe Evaluation Cycle

The current dry-run control loop is:

`Observation -> State -> Plan -> Decision -> Validation -> Safety -> Evaluation -> Telemetry -> no executor`

Only the explicit `noop` action is accepted. Disallowed actions are denied and recorded. This baseline must pass before Local AI or OpenAI providers are connected.
