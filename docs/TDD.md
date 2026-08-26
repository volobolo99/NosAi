# NosAi — Technical Design Document (TDD)

**Version:** 1.0  
**Project version observed:** 4.21.0  
**Status:** Engineering baseline / implementation guide

## 1. Purpose

NosAi is a source-grounded AI runtime for NosTale. The system must be observable, testable, reproducible and safe to evolve from offline/observation-only operation toward validated live-client integration.

This TDD defines the target architecture, component contracts, data flows, dashboard contract, testing strategy, CI/evidence model, security boundaries and implementation sequence.

The design separates **observation**, **decision**, **action validation**, and **action transport**. Detecting a game process must never by itself authorize control of the client.

## 2. Current repository baseline

The repository is source-first: runtime code is under `app/`, tests under `tests/`, and `pyproject.toml` is the package/configuration source of truth. The current roadmap is observation first, followed by validated perception, planning/reward integration and only later a separately gated action transport.

The package targets Python >=3.10 and exposes CLI entry points for preflight, pilot, client probing, diagnostics, dashboard and knowledge import. Development dependencies include pytest, pytest-cov, Ruff, NumPy, FastAPI/httpx, PyTorch and OpenCV.

The live-client boundary exposes `ClientAdapter` with `check_connection()`, `read_state()`, `validate_action()` and `close()`. The adapter contract validates actions without executing them.

The strategy layer models HP/MP, Dignity, grade differential, resistance, target information, time, SP/elemental signals, hardcore raid state and room objectives. Strategic assessment produces explicit priorities and reward metadata rather than hiding game assumptions inside a neural policy.

Primary repository sources: `README.md`, `pyproject.toml`, `app/client/adapter.py`, `app/nostale/strategy.py`, `docs/NOSTALE_STRATEGY_MODEL.md`.

## 3. Design principles

1. Source-derived mechanics remain hypotheses until validated.
2. Observation precedes action.
3. Components communicate through explicit contracts.
4. Important CI/test/security results are traceable to commit and artifact.
5. `NOT_RUN`, `PARTIAL`, `FAIL` and `PASS` are distinct states.
6. Structural changes are small and regression-tested.
7. Optimization starts from measurements.
8. Dependencies are added only for concrete capability.
9. Missing/stale/invalid state fails closed.
10. CI and local execution remain reproducible where practical.

## 4. High-level architecture

```text
                         +----------------------+
                         |      NosAi Core      |
                         +----------+-----------+
                                    |
                     normalized world/event state
                                    |
             +----------------------+----------------------+
             |                      |                      |
      +------v------+        +------v------+        +------v------+
      | Perception  |        | World State |        | Knowledge   |
      +------+------+        +------+------+        +------+------+ 
             |                      |                      |
             +----------------------+----------------------+
                                    |
                              +-----v-----+
                              |   Brain   |
                              +-----+-----+
                                    |
                              +-----v-----+
                              | Planner   |
                              +-----+-----+
                                    |
                         +----------+----------+
                         | Strategy / Reward  |
                         +----------+----------+
                                    |
                              Action proposal
                                    |
                         +----------v----------+
                         | Safety / Validator |
                         +----------+----------+
                                    |
                     +--------------+---------------+
                     |                              |
              observation-only               future gated transport
                     |                              |
              ClientAdapter                 Live action adapter
                     |
              Windows NosTale client

      +---------------------------------------------------------+
      |                   Observability Layer                    |
      | events | metrics | logs | evidence | diagnostics       |
      +---------------------------+-----------------------------+
                                  |
                         REST + WebSocket
                                  |
      +---------------------------v-----------------------------+
      |                    NosAi Dashboard                       |
      | Control Center | Runtime | Game View | Brain | Memory   |
      | Test Center | Diagnostics | Security | Sources | Config |
      +---------------------------------------------------------+

      CI -> tests -> JUnit/coverage -> security/SBOM -> artifacts
                                           |
                                           +-> Test Center evidence
```

## 5. Component responsibilities

### Perception
Converts raw client observations into normalized, timestamped observations. It does not decide actions. It owns acquisition, normalization, timestamps, confidence and stale/malformed-data rejection.

### World State
Maintains the current normalized game model and provenance: player, room/map, entities, target, skills/cooldowns, resources, objectives, timers, confidence and staleness. It must retain enough information to reproduce a decision from recorded evidence.

### Knowledge
Stores source-derived rules, observations, confidence and provenance. Each rule should record source, rule ID, confidence, validation times, evidence references and status (`hypothesis`, `validated`, `contradicted`, `deprecated`). Contradictory live observations are retained.

### Brain / Executive controller
Combines world state, memory, knowledge and goals into a decision context. It returns decision ID, goal, candidate strategies, selected strategy, confidence, rationale/evidence references, constraints, timestamp and latency. It does not directly execute client actions.

### Planner
Turns the selected strategy into validated action proposals such as movement, skill selection, consumable use, target selection, wait/reposition and objective transitions. Planning is constrained by safety, cooldowns, state validity and objective requirements.

### Strategy / Reward
`app/nostale/strategy.py` exposes explicit signals including resistance threshold, Dignity guard, low-HP guard, hardcore raid risk and room objective. Reward metadata carries source provenance. Future reward changes require regression/benchmark evaluation.

### Memory
Conceptually divided into working state, episodic events/results, semantic knowledge and evaluation/benchmark history. Writes are timestamped and attributable to a source/event. Uncertain observations must not silently become facts.

### Client boundary
`ClientAdapter` is the generic live-client contract: `check_connection()`, `read_state()`, `validate_action(action)`, `close()`. A concrete adapter must be explicitly configured. Process detection alone never authorizes live runtime. The current Windows adapter remains observation-only until perception/state validation is accepted.

### Safety
A separate gate between planning and any future action transport. It validates client connection, action schema, state freshness, policy constraints, cooldown/resource constraints, runtime mode and explicit authorization. Safety failure is fail-closed.

### Observability
Collects structured events, metrics, errors, decision traces, client diagnostics and test/CI evidence.

## 6. Canonical event model

All realtime consumers should use a common envelope:

```json
{
  "event_id": "uuid",
  "type": "skill_started",
  "timestamp": "ISO-8601",
  "tick": 12345,
  "source": "runtime",
  "confidence": 0.98,
  "correlation_id": "decision-uuid",
  "payload": {}
}
```

Recommended events: `runtime_state`, `world_state_updated`, `goal_changed`, `decision_created`, `action_proposed`, `action_validated`, `action_rejected`, `skill_started`, `skill_finished`, `effect_started`, `effect_finished`, `memory_write`, `reward_updated`, `progress_updated`, `suggestion_created`, `test_started`, `test_finished`, `ci_updated`, `security_updated`, `error`.

The dashboard uses WebSocket for realtime events and REST for snapshots/history.

## 7. Dashboard technical design

The dashboard should remain lightweight and browser-native: HTML, CSS, JavaScript, FastAPI, WebSocket and Canvas 2D initially. WebGL is added only when measured rendering needs justify it. Electron/React/Tauri are deferred unless a concrete requirement warrants the additional complexity.

Recommended pages under `app/dashboard/web/`:

```text
index.html
control_center.html
runtime.html
game_view.html
test_center.html
diagnostics.html
sources.html
brain.html
memory.html
settings.html
```

### Control Center
Expose runtime status, current goal, decision/confidence, perception/world/brain/planner/safety/memory pipeline, performance, errors, CI, security, SBOM, Test Center, AI progress, AI suggestions and live events.

### Test Center
Expose CI run/commit, gate states, test counts, JUnit, line/branch coverage, static analysis, security audit, SBOM, artifact IDs, evidence SHA/provenance, failures, `NOT_RUN` vs `PASS`, and historical trends.

### Game View
Render the observed character and effects without client-control logic in the browser:

```text
client assets / observations
        -> normalized manifest
        -> Canvas/WebGL renderer
        -> transparent character/effect layer
        -> dashboard
```

Every rendered asset needs source, asset ID, animation/effect ID, dimensions, frame rate, alpha availability and extraction/normalization version. If real assets are unavailable, show `ASSET_NOT_AVAILABLE`; never fake live state.

### AI Progress / Suggestions
Every suggestion must be traceable to a goal, confidence, reason, evidence references and timestamp. The dashboard must never invent progress when runtime data is unavailable.

## 8. API contract

Logical API surface:

```text
GET  /api/status
GET  /api/runtime
GET  /api/world-state
GET  /api/brain
GET  /api/memory
GET  /api/progress
GET  /api/suggestions
GET  /api/tests
GET  /api/test-center
GET  /api/security
GET  /api/sbom
GET  /api/sources
GET  /api/diagnostics
GET  /api/assets/character
WS   /ws
```

Responses should include schema/version, timestamp, status, data, provenance when applicable and explicit errors. Secrets and private credentials must never reach browser clients.

## 9. Character/effect pipeline

1. **Discovery:** identify configured client assets and animation/effect metadata without assuming undocumented layouts.
2. **Extraction:** convert source assets into a normalized internal representation.
3. **Manifest:** map character -> animation -> frames, skill -> animation/effect -> frames, entity -> sprite -> metadata.
4. **Rendering:** Canvas 2D baseline; WebGL only for measured high-cost effects.
5. **Synchronization:** `skill_started`/`effect_started` events select animations using timestamps.

The visual pipeline is separate from AI decision logic.

## 10. Test architecture

### L0 — syntax/import
Python compilation, package import, configuration parsing.

### L1 — unit
Pure functions, strategy rules, validators, parsers and state transitions.

### L2 — contract
ClientAdapter, event schemas, REST schemas, WebSocket events and evidence schemas.

### L3 — integration
Perception -> world state -> brain -> planner -> safety, runtime -> dashboard and CI artifact -> Test Center.

### L4 — regression/benchmark
Complete regression suite, deterministic scenarios, performance baselines and strategy/goal success metrics.

Live-client tests remain separately gated and observation-only until the state pipeline is proven.

## 11. Test Center evidence contract

Canonical state machine:

```text
NOT_RUN -> RUNNING -> PASS
                   -> FAIL
                   -> PARTIAL
```

`CANCELLED` may be retained as an execution outcome but normalizes to `NOT_RUN` for capability coverage.

Missing JUnit/coverage because a stage did not run must be reported as `NOT_RUN`, never as zero tests or implicit PASS.

Minimum evidence shape:

```json
{
  "schema": 3,
  "commit": "sha",
  "run_id": "id",
  "ci": {},
  "junit": {},
  "coverage": {},
  "security": {},
  "sbom": {},
  "artifact": {}
}
```

Test Center must never claim PASS for a stage that was skipped.

## 12. CI/CD design

Preferred pipeline:

```text
checkout
  -> install
  -> pip check
  -> static analysis
  -> import smoke
  -> pytest
  -> JUnit
  -> coverage
  -> CLI smoke
  -> security audit
  -> SBOM
  -> evidence
  -> immutable artifacts
  -> Test Center snapshot
```

Quality and security failures remain independently visible. Test Center persistence must not mask the upstream failure and must not fail merely because an upstream evidence artifact is absent. CI actions should use valid immutable references and be updated deliberately.

## 13. Security model

Controls include dependency audit, SBOM, least-privilege GitHub permissions, pinned CI actions, no secrets in frontend assets, explicit client-adapter configuration, observation-only live boundary, action validation before future transport, structured audit evidence and fail-closed behavior.

A detected dependency vulnerability is a security gate failure until resolved, explicitly risk-accepted with documentation, or proven non-applicable.

## 14. Performance requirements

Initial engineering targets, to be revised from real baselines:

| Area | Target |
|---|---:|
| Dashboard initial load | < 2 s |
| Local REST snapshot | < 150 ms p95 |
| Local WebSocket propagation | < 100 ms p95 |
| Dashboard idle CPU | < 5% typical desktop CPU |
| Dashboard idle memory | < 250 MB |
| Game View | 60 FPS target when source permits |
| Evidence generation | < 10 s excluding test execution |

These are engineering targets, not CI gates, until a benchmark harness records real measurements by environment and revision.

## 15. Data retention and provenance

Retain runtime event IDs, decision traces, source references, test results, CI run IDs, artifact IDs/names, commit SHA, benchmark results and contradictions between source rules and observations. Historical evidence must not be silently rewritten to match current rules.

## 16. Failure handling

Explicit failure states should include:

```text
CLIENT_NOT_FOUND
CLIENT_NOT_READY
STATE_STALE
INVALID_STATE
PERCEPTION_LOW_CONFIDENCE
KNOWLEDGE_CONTRADICTION
PLANNER_REJECTED
SAFETY_REJECTED
TEST_NOT_RUN
EVIDENCE_MISSING
SECURITY_FAILED
ARTIFACT_MISSING
```

The dashboard should surface the first causal failure prominently and list downstream consequences separately.

## 17. Implementation roadmap

### Phase 1 — foundation
- keep configuration single-sourced;
- finish dashboard modularization;
- finish Test Center evidence semantics;
- keep CI artifacts/provenance reliable.

### Phase 2 — runtime observability
- unify event envelopes;
- expose world state, brain, planner, memory and progress snapshots;
- add realtime metrics and decision traces.

### Phase 3 — validated perception
- Windows client observation;
- screenshot/state acquisition;
- normalized state;
- confidence/staleness;
- observation regression corpus.

### Phase 4 — strategy/planning validation
- connect validated state to strategy assessment;
- connect strategy to planner/reward;
- benchmark room objectives;
- preserve source provenance.

### Phase 5 — Game View
- client asset discovery;
- normalized sprite/effect manifests;
- Canvas renderer;
- realtime skill/effect synchronization;
- performance measurements.

### Phase 6 — separately gated action transport
Only after observation and state validation are accepted: transport contract, action dry-run tests, safety tests, explicit authorization and live integration tests.

### Phase 7 — hardening
Security closure, full CI green, benchmark baselines, artifact verification and release checklist.

## 18. Definition of Done

A feature is complete only when applicable: implementation exists; contract tests exist; unit/integration tests pass; static analysis passes; security is assessed; evidence is generated; artifact provenance matches commit; dashboard exposes operational state; failure states are explicit; performance impact is measured where relevant; and source-derived assumptions are documented and traceable.

For live-client functionality, observation must be validated before action transport is enabled.

## 19. Architectural decisions

### AD-001 — HTML/JS dashboard
Lightweight, portable and aligned with the existing FastAPI/WebSocket dashboard. Desktop wrappers are deferred.

### AD-002 — REST + WebSocket
REST is authoritative for snapshots/history; WebSocket is authoritative for realtime event delivery.

### AD-003 — Canvas 2D first
Minimizes dependencies and is sufficient for the first transparent character/effect renderer. WebGL is introduced only when measured requirements demand it.

### AD-004 — Observation-only client boundary
Prevents process detection from being confused with authorization to control the game and matches the existing ClientAdapter/live-client roadmap.

### AD-005 — Evidence-first CI
CI results are explicit evidence with commit/run/artifact provenance. Missing execution is `NOT_RUN`, never implicit PASS.

## 20. Open engineering questions

1. Which Windows observation mechanism gives the most stable normalized state without assuming undocumented offsets?
2. Which client assets can technically and legally be extracted for Game View?
3. Which world-state fields can be verified from live observation versus source-derived inference?
4. What benchmark suite measures decision quality without coupling the system to one route/map?
5. What retention period is appropriate for raw observations, screenshots and decision traces?
6. Which performance limits should become hard CI gates after real baselines exist?

These remain intentionally unresolved until evidence is available.

## 21. Reference documents

- `README.md` — repository baseline and live-client roadmap.
- `pyproject.toml` — packaging, dependencies, CLI entry points and test/static configuration.
- `docs/NOSTALE_STRATEGY_MODEL.md` — source-derived strategy model and validation policy.
- `app/client/adapter.py` — live-client contract.
- `app/nostale/strategy.py` — strategy state/assessment/reward metadata.
- `.github/workflows/` — CI/security/evidence implementation.
- `tests/` — executable regression and contract specifications.

## 22. Acceptance statement

This document is the engineering target, not a claim that every component is already implemented. Actual implementation status must always be checked against repository code and CI evidence. Future/gated components must remain clearly represented as such in the dashboard and Test Center.
