# NosAi — Windows Sandbox + Replay + Regression

## Purpose

This block provides the disposable execution boundary for researched/generated candidates and couples it to protected replay and anti-forgetting regression.

## Execution boundary

`WindowsSandboxBackend` targets the Windows Sandbox CLI (`wsb`) available with the newer Windows Sandbox experience on Windows 11 24H2+.

Security defaults:

- network disabled;
- vGPU disabled;
- clipboard redirection disabled;
- candidate workspace mapped read-only;
- output directory mapped writable only for evidence;
- sandbox session disposable;
- host repository is never used as the candidate workspace.

The backend fails closed with `NOT_RUN` when Windows Sandbox/CLI is unavailable. A `NOT_RUN` result is never promotable.

Microsoft documents that Windows Sandbox is disposable and hardware-isolated through the Hyper-V hypervisor. Microsoft also documents that networking is enabled by default, so NosAi explicitly disables it. Mapped folders are treated as a security boundary and the candidate workspace is therefore read-only. See the official Windows Sandbox documentation before enabling the runtime on a target machine.

## Replay

`ReplayStore` remains append-only for protected scenarios. `ReplayRunner` executes an injected deterministic evaluator and records each case independently. A replay exception becomes a failed result instead of terminating the suite.

Expected fields are compared as a subset so runtime telemetry may grow without changing every protected case.

## Regression

`CandidateRegressionSuite` combines:

1. protected replay;
2. anti-forgetting score comparison;
3. per-case evidence.

A candidate is acceptable only when both replay and anti-forgetting gates pass.

## Current limitation

Windows Sandbox is a clean Windows environment. It does not automatically contain the complete NosAi Python environment. The production executor therefore requires a prepared, immutable runtime payload (for example a validated portable Python/runtime bundle) before real candidate execution can be considered PASS. The repository currently contains the backend and contracts, but this Windows-host integration must still be exercised on an actual Windows 11 24H2+ machine.

## Promotion rule

`simulation PASS` is insufficient for `main`.

The intended chain is:

`candidate -> Windows Sandbox -> protected replay -> regression -> anti-forgetting -> Windows real -> NosTale real -> explicit confirmation -> main`

No step may silently substitute for a missing later step.
