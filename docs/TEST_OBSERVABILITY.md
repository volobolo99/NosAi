# NosAi Test Observability

## Purpose

The dashboard Test Center is the verification control plane. It aggregates source inventory, AST parsing, symbols, imports, communication edges, test associations, CI evidence and quality gates. It does not replace CI.

## Traceability

Every source unit follows:

`requirement -> producer -> artifact -> consumer -> assertion -> evidence -> gate`

A result is complete only when the boundary is identified, the check executes, evidence is recorded and the result is traceable to the smallest useful file/symbol/process boundary.

## Questions for every file

1. What is its responsibility?
2. Who imports or invokes it?
3. What is its public contract?
4. What inputs can be malformed, empty or stale?
5. What outputs are produced?
6. Which consumers use those outputs?
7. Which invariants must survive the boundary?
8. Which tests prove them?
9. What happens on exception, timeout or missing dependency?
10. Is the code reachable, duplicated or obsolete?
11. Is file size/complexity proportional to its responsibility?
12. Does any comment, documentation or logging add no operational value?

## Dashboard levels

- **L0 System:** gates, failures, coverage, dependency risk, repository size and readiness.
- **L1 Domain:** brain, perception, memory, client, dashboard, knowledge, runtime and infrastructure.
- **L2 File:** LOC, bytes, imports, dependants, symbols, tests, failures and risk.
- **L3 Symbol:** functions/classes, callers, callees, branches and tests.
- **L4 Communication:** directed module/process edges with input/output contract and validation evidence.
- **L5 Test:** exact test, expected/actual result, duration, traceback and affected boundary.

## Gates

- **G0:** inventory
- **G1:** syntax/build/import
- **G2:** static/security/dependency
- **G3:** unit/contract/integration
- **G4:** runtime/E2E/CLI
- **G5:** safety/observation-only boundary
- **G6:** coverage/mutation/complexity/size/duplication

Allowed states are `PASS`, `FAIL`, `WARN`, `NOT_RUN`. `NOT_RUN` is never equivalent to `PASS`.

## Minimality and weight

The Test Center must flag oversized files, duplicate modules, unused imports, generated artifacts, duplicated configuration, unused dependencies and tests without meaningful assertions. Signals produce remediation candidates; they never trigger automatic deletion.

## Continuous loop

`scan -> map -> test -> compare -> explain -> gate -> record -> rescan`

AST inventory is the first layer. Runtime coverage, JUnit results, dependency/SBOM reports and benchmark history are evidence layers that must be attached to the same file/process graph as they become available.

## Evidence policy

Line coverage measures execution, not correctness. Branch/contract coverage is preferred for decision-heavy code and mutation testing is reserved for high-risk boundaries. Dependency inventory should include direct and transitive components and be automated in CI. This aligns with OWASP SCVS control families for inventory, SBOM, build environment, package management, component analysis and provenance. Continuous assurance is preferred over one-time verification.

## Safety

The Test Center is observation-only. It must never provide an action-execution control path. Any future action transport requires an independent gate, explicit authorization and separate validation.
