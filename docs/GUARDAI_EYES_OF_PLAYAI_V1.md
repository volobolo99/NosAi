# GuardAi — EYES OF PLAYAI v1.0

> Canonical integration specification for the GuardAi live-observation, strategy, research, failure-learning and autonomy layer.

## Purpose

`EYES OF PLAYAI` is the user-facing live perception and supervision layer of `GuardAi` on the dedicated Realme X50 Pro. It exposes the game view consumed by PlayAi together with perception, reasoning, decisions, probabilities, mission state, Guardian analysis and replay context.

## Architecture

```text
NosTale Client
   -> Game Capture / Adapter
      -> PlayAi Vision / Perception
      -> PerceptionFrame
      -> Decision Fabric
         -> PlayAi
         -> GuardAi (Critic / Predictor / Risk / Strategy / Research)
      -> Knowledge / Memory
      -> Cloud Control Plane
      -> Realme X50 Pro / EYES OF PLAYAI
```

The control/data plane and video plane are separate.

### Control/data plane

Authenticated realtime messaging carries session state, heartbeats, mission state, perception metadata, decisions, alerts, strategy updates, replay markers and knowledge/version notifications. For Supabase Realtime, Broadcast is the preferred low-latency ephemeral channel; Presence is for slow-changing connection/session state; Postgres Changes is for durable database-driven changes rather than high-frequency telemetry.

### Video plane

A dedicated low-latency stream, initially WebRTC-oriented, carries the live game view. The video channel can degrade independently without disabling control/safety. Target profiles are high-quality/60 fps, 720p/30 fps and degraded telemetry-only mode; exact codec, bitrate and TURN topology are benchmark decisions.

## PerceptionFrame contract

Each visual state is correlated with a stable frame/event identity:

```text
frame_id, timestamp, source_id, stream timestamp,
player box, objects, classes, confidence, targets,
objectives, danger zones, paths, strategy_id,
candidate actions, selected action, action confidence,
context_id, decision_id, protocol_version
```

The Realme overlay uses frame identity/timestamp to keep annotations synchronized with the game image.

## Eyes of PlayAi overlay

Three layers are mandatory:

1. **PERCEPTION** — what PlayAi believes it sees: player, enemies, NPCs, items, objectives, obstacles, paths and danger zones.
2. **REASONING** — what PlayAi evaluates: threats, candidate actions, routes, reward, time, cost, risk and alternatives.
3. **DECISION** — selected action, strategy, success probability, confidence, expected time, risk and reason.

GuardAi may independently inspect the same state. A disagreement is an auditable event and may trigger re-perception, deeper analysis or Decision Fabric arbitration; GuardAi does not silently overwrite PlayAi perception.

## Mission Solver

Adaptive analysis depth:

```text
FAST  -> validated local knowledge + current state
SMART -> targeted research for missing information
DEEP  -> research + simulation + alternatives + benchmark
```

The result contains recommended route/method, expected time, success probability, confidence, risk, resource cost and alternatives. Selection balances success, confidence, time, risk and cost rather than maximizing one number blindly.

## Failure Lab

Every useful failure becomes evidence:

```text
FAIL -> capture state/actions/context -> causal analysis
     -> classify -> generate alternatives -> test/benchmark
     -> retry when justified -> validate -> Knowledge Candidate
```

Failure classes: strategy, execution, missing information, environment/randomness. The system avoids infinite retries by declaring insufficient evidence or exhausted strategy space when appropriate.

## Strategy Lab and Knowledge Transfer

Strategies are tracked as CURRENT, BEST, ALTERNATIVE, EXPERIMENTAL or RETIRED. Promotion is:

```text
Experimental -> Sandbox -> Benchmark -> Stable Candidate
-> NosAi validation -> Approved/Rejected -> Local Capability
```

Validated Knowledge Packs move into NosAi local knowledge so future decisions can work offline without repeatedly calling GuardAi.

## Probability and impact metrics

No improvement percentage is invented. Core metrics are:

```text
Success Rate = successful / total attempts
Error Reduction = (baseline errors - current errors) / baseline errors
Time Improvement = (baseline time - current time) / baseline time
Prediction Error = actual outcome - predicted outcome
Guardian Dependency Index = share of validated decisions/capabilities requiring GuardAi
Guardian Impact Score = weighted measured improvement against a controlled baseline
```

User-facing estimates must include sample count and confidence/reliability status. Small samples are explicitly preliminary.

## Autonomy and saturation

GuardAi is designed to reduce permanent dependency. A Strategy Saturation Engine detects diminishing returns from new strategies without stopping contextual decision-making. Even at high autonomy, GuardAi remains an auditor, researcher, safety monitor and strategy laboratory.

## Patch & Research Cycle

On game update detection or manual refresh:

```text
version change -> identify affected knowledge -> source-grounded research
-> compare mechanics/strategies -> benchmark -> update Knowledge Packs
-> validate against replay/scenarios -> restore maximum validated autonomy
```

## Realme UI modes

- **Player View:** clean live game with essential information.
- **Engineer View:** complete perception, reasoning, decision, path, threat, probability, GuardAi and telemetry overlays.
- **Event Focus:** automatically focuses anomalies/disagreements/failures and exposes replay/analysis.

A rolling replay buffer may retain recent frames/telemetry. Important events create markers combining video, perception, decision, GuardAi analysis, world state and outcome.

## Security and safety

- Realme sessions are authenticated and bound to the intended NosAi/GuardAi instance.
- Private realtime channels and least privilege are required.
- GuardAi cannot bypass Decision Fabric, Safety Gate or Human Override.
- Live viewing does not grant direct game-action authority.
- No anti-cheat evasion is part of this design.
- Video loss cannot silently disable control/safety.

## Existing NosAi integration

The existing observation-only pipeline remains the foundation: `WindowsNosTaleAdapter -> WindowsNosTalePerception -> live_character_view -> /api/character-view -> dashboard canvas`. EYES OF PLAYAI extends this pipeline rather than replacing it.

## Implementation order

1. Freeze PerceptionFrame/telemetry contract.
2. Extend the existing live character view into synchronized Eyes of PlayAi frames.
3. Add low-latency stream transport and session authentication.
4. Build Realme Player View.
5. Add Engineer View overlays.
6. Add Mission Solver telemetry.
7. Add Failure Lab/replay integration.
8. Add Strategy Lab and probability metrics.
9. Add Knowledge Pack promotion and autonomy metrics.
10. Add patch/research triggers.
11. Benchmark latency, CPU/RAM, network and battery.
12. Add Test Center/CI and promote only after gates pass.

## Definition of Done

EYES OF PLAYAI v1.0 is complete when the Realme securely connects to its GuardAi session; the user can view the live game from PlayAi's visual perspective; perception/reasoning/decision overlays are synchronized; disagreements are auditable; mission recommendations expose time/success/confidence/risk; failures produce learning evidence; validated strategies transfer to local knowledge; impact/dependency metrics are measurable; important decisions are replayable; video loss cannot compromise control/safety; and NosAi can operate offline using validated local knowledge.
