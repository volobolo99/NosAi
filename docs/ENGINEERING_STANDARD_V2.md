# NosAi Engineering Standard V2

## Purpose

This document defines the default engineering method for NosAi development work. It applies to future programming changes unless a task explicitly requires a different workflow.

## 1. Evidence-first development

Every change starts from the current repository state, the active branch, existing tests, architecture contracts, and the relevant uploaded project sources. No implementation is considered complete from code inspection alone.

Required sequence:

1. inspect the current repository and affected modules;
2. inspect existing tests and CI gates;
3. research authoritative documentation and high-signal open-source implementations;
4. compare alternatives and select the smallest robust design;
5. implement on `develop/nosai-next` or a dedicated feature branch;
6. run static checks and deterministic tests;
7. run integration and regression tests;
8. run Windows/NosTale real-host tests when the feature depends on them;
9. record exact evidence and observed failures;
10. only promote to `main` after validation and explicit confirmation.

## 2. External code and project reuse

External projects may be used as references or dependencies only after checking:

- repository license and compatibility;
- maintenance/activity and release status;
- security and supply-chain risk;
- API stability;
- architectural fit;
- test quality;
- whether the same behavior can be implemented more simply inside NosAi.

Prefer established libraries over copied code. If code is reused, preserve required license/notice obligations and record provenance in the implementation notes. Never copy code merely because it passes a search result.

Current research patterns selected for NosAi include property-based testing (Hypothesis), static typing (Pyright), structural/static analysis (Semgrep), OpenTelemetry-style traces/metrics/logs, Windows Application Verifier where applicable, and ephemeral isolated execution patterns inspired by modern software-agent sandboxes. These are design references, not automatic dependencies.

## 3. Test separation

Evidence classes are immutable:

- `REAL`: collected from the user's real Windows host/client/session;
- `CI`: collected from GitHub or another controlled CI environment;
- `SIMULATED`: collected inside an isolated simulation/sandbox.

A CI or simulation result can never be promoted to `REAL` by inference.

## 4. Test output rules

The test system reports observations, not remediation advice. A finding must identify the exact condition, expected condition, observed value, error type/message, source location when known, environment, timestamp, correlation ID, and evidence artifacts. It must not decide how the developer should fix the problem.

## 5. Automatic failure investigation

A failed test may trigger the Simulation & Repair Research pipeline. That pipeline is separate from the test result itself. It may research possible explanations and candidate changes, but its output is labelled `RESEARCH/SIMULATION` and never changes production code automatically.

## 6. Promotion policy

`main` contains only explicitly confirmed versions. `develop/nosai-next` contains the current integration candidate. Candidate changes are promoted only after all required gates are green and the user explicitly confirms the version.
