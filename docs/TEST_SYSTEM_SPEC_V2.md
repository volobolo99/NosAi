# NosAi Test System V2 — Evidence-First Specification

## Purpose

The test system is an evidence collector and reporter. It must **not decide how to fix a problem**. Every result describes what was tested, what was observed, the exact failure or finding, and the evidence location.

The system distinguishes three evidence classes:

- `REAL`: collected from the user's real Windows host and real NosTale client/session.
- `CI`: collected in GitHub Actions or another controlled CI environment.
- `SIMULATED`: produced by a simulator/mock/replay. Never presented as real runtime evidence.

A result may never be promoted from `CI` or `SIMULATED` to `REAL` by inference.

## Test layers

1. **Host / Windows** — OS version/build, architecture, CPU, RAM, GPU, display, locale, permissions, Python/runtime, drivers, processes, services, firewall/network state where permission allows.
2. **NosTale client** — executable identity, process/PID, window identity/geometry, client version/build when observable, session state, launcher state, resource paths, crash/exit state.
3. **Connectivity** — DNS, TCP/HTTPS endpoints explicitly configured by NosAi, latency, timeout, TLS/certificate observations, API reachability and response metadata. Secrets and tokens are sanitized.
4. **Client observation** — screenshots/frame capture metadata, perception pipeline, entity detection, minimap/world state, player state, skills, packet observations only where legally/configurationally permitted.
5. **NosAi runtime** — launcher, runtime bridge, adapter lifecycle, state acquisition, event flow, telemetry, diagnostics, dashboard/API health.
6. **AI modules** — contracts and execution of brain, planning, memory, knowledge, perception, multi-agent, learning, RL, strategy, reward, self-repair and evaluation components.
7. **Services / plugins / integrations** — each configured dependency is independently tested and reported with its identity, endpoint/provider, connection state and observed error.
8. **Code execution quality** — syntax/compile errors, exceptions, failed assertions, type/contract violations, static-analysis findings, unreachable/dead code signals, deprecations, warnings and runtime anomalies. Findings describe the observed issue only; no remediation advice is emitted.
9. **End-to-end scenarios** — ordered real-host scenarios with preconditions, timestamps, observed transitions, expected contract, actual observation and evidence references.
10. **Regression / release** — comparison with the previous confirmed baseline and candidate commit; changed tests, newly failing tests and environmental deltas.

## Result contract

Every test result uses the following fields where applicable:

- `id` — stable unique finding/result ID.
- `timestamp_utc` — collection time.
- `source` — `windows-local`, `github-ci`, `simulator`, or other explicit source.
- `evidence_class` — `REAL`, `CI`, or `SIMULATED`.
- `test_suite`, `test_case` — exact test identity.
- `component` — component under test.
- `severity` — `BLOCKER`, `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`.
- `status` — `PASS`, `FAIL`, `ERROR`, `SKIPPED`, `BLOCKED`, `NOT_RUN`, `WARNING`, `INFO`.
- `observed` — precise factual observation.
- `expected` — expected contract/condition, when defined.
- `actual` — actual value/state, when defined.
- `error_type` — exact exception/error category when present.
- `error_message` — exact sanitized error message.
- `file`, `line`, `column` — source location when applicable.
- `stack_trace` — sanitized stack trace when applicable.
- `environment` — host/runtime/client metadata.
- `evidence` — artifact IDs, screenshots, logs, traces, hashes.
- `duration_ms` — measured duration where applicable.
- `correlation_id` — ties related observations across suites.
- `baseline` — previous reference identity when regression-tested.

## No-fix policy

The reporter may state **what is wrong, where it occurred, under what condition, and what evidence proves it**. It must not state "fix by", "change X to Y", "recommended solution", or equivalent remediation language.

## Real Windows/NosTale requirement

The real-host suite runs from a local Windows test agent on the user's machine. GitHub-hosted Linux/Windows runners are CI evidence only. A real NosTale result requires a real process/session observation and host metadata collected by the local agent.

The local agent sends sanitized evidence to the dashboard/Test Center and can optionally package a complete report for publication to GitHub.

## Report lifecycle

`COLLECTING -> COMPLETE -> SEALED -> PUBLISHED`

A report is immutable after sealing. Publication creates a deterministic artifact containing:

- `report.json` — machine-readable complete report;
- `report.md` — human-readable report;
- `manifest.json` — report metadata and SHA-256 hashes;
- optional sanitized logs/screenshots/traces.

## Dashboard annotations panel

The dashboard contains a persistent **Test Annotations** panel. It shows every finding, including PASS/INFO records when configured, with filters for evidence class, severity, component, suite, status and timestamp. Each row exposes the exact error/finding, source location, environment and evidence references.

The panel does not rewrite or interpret the finding into a proposed fix.

## Submit Report

The test-only dashboard exposes **Invia report**. Clicking it seals the current report, creates the report bundle, verifies hashes, and submits the bundle to the configured NosAi GitHub repository as a test artifact. Publication must target a test-report path/branch and never write to `main`.

The dashboard must clearly show publication status and the resulting GitHub commit/artifact identifier. Credentials are never stored in the report and are never rendered in the UI.
