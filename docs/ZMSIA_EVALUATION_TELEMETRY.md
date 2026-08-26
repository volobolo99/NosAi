# ZMSIA Evaluation + Telemetry

This layer is intentionally deterministic and pre-execution.

## Flow

Observation -> State -> Plan -> Decision -> Validation -> Safety -> Evaluation -> Telemetry -> Executor

The current evaluation gate accepts only `noop` actions. It is not a production policy; it establishes a measurable, provider-neutral dry-run baseline before Local AI or OpenAI is introduced.

Telemetry is append-only in the in-memory test sink. Future persistent telemetry must preserve cycle IDs, provenance, timestamps, decisions, safety outcomes, and evaluation results.

## Next gate

After this slice is tested, integrate the gate into the orchestrator. Only then add the Local provider, followed by OpenAI behind the same `DecisionProvider` contract.
