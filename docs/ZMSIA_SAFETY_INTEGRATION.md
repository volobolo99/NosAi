# ZMSIA safety integration

The safety gate is now part of the orchestration path:

`Observation -> State -> Plan -> Decision -> Action Validation -> Safety Policy -> authorization result`

The orchestrator still does **not** execute actions. The result is an explicit authorization decision for a future executor.

## Policy

The initial policy is deny-by-default. Only `noop` is allowed in the dry-run profile.

## Required next layer

Add evaluation and telemetry around the safe cycle before enabling any Local or OpenAI decision provider or client executor.
