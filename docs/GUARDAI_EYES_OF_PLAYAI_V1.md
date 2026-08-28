# GuardAi — EYES OF PLAYAI v1.0

> Canonical integration specification for the GuardAi live-observation, strategy, research, failure-learning and autonomy layer.

## 1. Purpose

`EYES OF PLAYAI` is the user-facing live perception and supervision layer of `GuardAi` on the dedicated Realme X50 Pro. It is not a duplicate of the PC dashboard and it is not a video-only remote viewer.

The system exposes, in near real time:

- the game view consumed by PlayAi;
- PlayAi perception objects and confidence;
- reasoning/strategy state;
- candidate actions and probabilities;
- selected next action;
- mission progress and ETA;
- GuardAi independent observations and disagreements;
- alerts, failures and replay context.

The broader GuardAi architecture remains: Guardian + Strategist + Researcher + Trainer.

## 2. Architectural position

```text
                         NosTale Client
                              |
                       Game Capture / Adapter
                              |
                +-------------+-------------+
                |                           |
           PlayAi Vision              Live Video
                |                           |
         Perception Frame             Video Gateway
                |                           |
                +-------------+-------------+
                              |
                       Decision Fabric
                              |
             +----------------+----------------+
             |                                 |
           PlayAi                           GuardAi
             |                                 |
       decision/action        critic/predictor/risk/strategy/research
             |                                 |
             +----------------+----------------+
                              |
                       Knowledge / Memory
                              |
                    Cloud Control Plane
                              |
                    Realme X50 Pro / GuardAi
                              |
                    EYES OF PLAYAI UI
```

## 3. Control plane vs video plane

The database is not used as a video transport.

### Control/data plane

Use authenticated realtime messaging for:

- session state;
- heartbeats;
- mission state;
- perception metadata;
- decision metadata;
- alerts;
- strategy updates;
- replay markers;
- knowledge/version notifications.

For Supabase Realtime, Broadcast is preferred for low-latency ephemeral events and filtered fan-out; Presence is reserved for slowly changing connection/session state. Postgres Changes is appropriate for durable database-driven changes, not high-frequency telemetry.

### Video plane

Use a dedicated low-latency streaming path, initially WebRTC-oriented, for the live game frames. The stream must be independently degradable from the control channel.

Video quality policy:

```text
GOOD       -> high quality / 60 fps target
MEDIUM     -> 720p / 30 fps target
POOR       -> reduced resolution/bitrate
VERY POOR  -> telemetry + event mode; control remains alive
```

The exact codec, bitrate and TURN topology are implementation choices to be benchmarked on the actual Realme/network.

## 4. Perception Frame contract

Each live visual state should be correlated with a stable frame/event identity.

```text
PerceptionFrame
- frame_id
- timestamp
- source_id
- image/stream timestamp
- player bounding box
- detected objects
- object classes
- object confidence
- targets
- objectives
- danger zones
- navigation/path candidates
- current strategy id
- candidate actions
- selected action
- action confidence
- context_id
- decision_id
- protocol_version
```

The Realme overlay uses the frame identity/timestamp to keep visual annotations synchronized with the game image.

## 5. Three information layers

### PERCEPTION

What PlayAi believes it sees:

- player;
- enemies;
- NPCs;
- items;
- objectives;
- obstacles;
- doors/paths;
- danger zones.

Every derived perception should carry confidence/provenance when available. The system must not invent a skill name or object identity when the adapter cannot support it reliably.

### REASONING

What PlayAi is evaluating:

- threats;
- candidate actions;
- routes;
- expected reward;
- time;
- cost;
- risk;
- alternative strategies.

### DECISION

What PlayAi selected:

- next action;
- selected strategy;
- success probability;
- confidence;
- expected time;
- risk;
- decision reason.

## 6. Guardian second opinion

GuardAi may independently inspect the same frame/context and compare its interpretation with PlayAi.

Example:

```text
PlayAi: enemy confidence 71%
GuardAi: enemy confidence 96%
=> PERCEPTION DISAGREEMENT
=> request recheck / escalate according to risk policy
```

GuardAi must not silently overwrite PlayAi perception. A disagreement becomes an auditable event and may trigger re-perception, deeper analysis or Decision Fabric arbitration.

## 7. Mission Solver

For a mission request, GuardAi uses adaptive analysis depth:

```text
FAST  -> validated local knowledge + current world state
SMART -> targeted research for missing information
DEEP  -> research + simulation + alternative strategies + benchmark
```

The output is a structured mission plan:

- recommended method/route;
- estimated completion time;
- success probability;
- confidence;
- risk;
- expected resource cost;
- alternatives.

The selection objective is not simply maximum success probability. It balances success, confidence, time, risk and cost according to mission policy.

## 8. Failure Lab

Failures are constructive learning events.

```text
FAIL
 -> capture state/actions/context
 -> causal analysis
 -> classify failure
 -> generate alternatives
 -> test/benchmark
 -> retry when justified
 -> validate result
 -> create knowledge candidate
```

Failure classes:

- strategy failure;
- execution failure;
- missing-information failure;
- environment/randomness failure.

A failed attempt must improve the evidence base whenever the captured data is sufficient. The system must avoid infinite retries by declaring the strategy space exhausted or the evidence insufficient when appropriate.

## 9. Strategy Lab

GuardAi maintains distinct strategy states:

- CURRENT;
- BEST;
- ALTERNATIVE;
- EXPERIMENTAL;
- RETIRED.

New strategies are not promoted directly into production behavior.

Promotion pipeline:

```text
Experimental
 -> Sandbox
 -> Benchmark
 -> Stable Candidate
 -> NosAi A/B validation
 -> Approved / Rejected
 -> Local Capability
```

The system may use deterministic search, beam search, Monte Carlo/MCTS and later learning/self-play methods only when the simulator, reward model and evaluation data are sufficiently trustworthy.

## 10. Probability and impact measurement

No user-facing improvement percentage may be fabricated.

Core measurements include:

```text
Success Rate = successful attempts / total attempts

Error Reduction = (baseline errors - current errors) / baseline errors

Time Improvement = (baseline time - current time) / baseline time

Prediction Error = actual outcome - predicted outcome

Guardian Dependency Index = share of validated decisions/capabilities requiring GuardAi

Guardian Impact Score = weighted measured improvement against a controlled baseline
```

Every estimate should expose sample count and confidence/reliability status. Small samples must be marked as preliminary.

## 11. Autonomy and Knowledge Transfer

GuardAi is designed to reduce, not increase, permanent dependency.

```text
GuardAi discovers/solves
        -> Knowledge Pack
        -> validation
        -> local promotion
        -> NosAi capability
        -> dependency decreases
```

The local PC remains the primary operational knowledge store for validated capabilities. The cloud is a synchronization and coordination layer, not the permanent brain.

## 12. Saturation

A Strategy Saturation Engine detects diminishing returns from new strategies. Saturation means the currently explored strategic space is no longer producing meaningful improvements; it does not disable ongoing contextual decision-making.

NosAi continues to calculate the best action for the current state even when the strategic library is saturated.

## 13. Patch & Research Cycle

When a game update/patch is detected or the operator requests a refresh:

```text
version change
 -> identify affected knowledge
 -> official/source-grounded research
 -> compare mechanics/strategies
 -> benchmark candidates
 -> update knowledge packs
 -> validate against replay/scenarios
 -> restore maximum validated autonomy
```

GuardAi remains active after autonomy reaches a high level: it becomes primarily auditor, researcher, safety monitor and strategy laboratory.

## 14. Live UI modes on Realme

### Player View

Minimal overlay for simply watching PlayAi.

### Engineer View

Full diagnostic mode:

- game image;
- perception boxes;
- confidence;
- path candidates;
- threat map;
- candidate actions;
- probabilities;
- current strategy;
- decision tree summary;
- GuardAi comparison;
- latency/resource telemetry.

### Event Focus

On anomaly, disagreement or failure, GuardAi can focus the relevant region, display the event, start/mark replay capture and expose the analysis.

## 15. Replay and debugging

A short rolling buffer may retain recent frames/telemetry. Important events create replay markers.

Failure replay combines:

```text
video frame
+ perception frame
+ PlayAi decision
+ GuardAi analysis
+ world state
+ outcome
```

This is the bridge between EYES OF PLAYAI and Failure Lab.

## 16. Security and safety

- Realme sessions are authenticated and bound to the intended NosAi/GuardAi instance.
- Private realtime channels and least-privilege authorization are required.
- GuardAi cannot bypass Decision Fabric, Safety Gate or Human Override.
- Live viewing does not grant direct game-action authority.
- No anti-cheat evasion mechanisms are part of this design.
- Video loss must never silently disable the safety/control plane.

## 17. Existing NosAi integration

The existing repository already contains an observation-only live character pipeline:

`WindowsNosTaleAdapter → WindowsNosTalePerception → live_character_view → /api/character-view → dashboard canvas`.

This remains the foundation for the first visual implementation. The existing pipeline is explicitly observation-only and does not inject actions or patch process memory. EYES OF PLAYAI extends this foundation rather than replacing it.

## 18. Implementation order

1. Freeze the PerceptionFrame/telemetry contract.
2. Extend existing live character view into synchronized Eyes of PlayAi frames.
3. Add low-latency stream transport and session authentication.
4. Build Realme Player View.
5. Add Engineer View overlays.
6. Add Mission Solver telemetry.
7. Add Failure Lab/replay integration.
8. Add Strategy Lab and probability metrics.
9. Add Knowledge Pack promotion and autonomy metrics.
10. Add patch/research triggers.
11. Benchmark latency, CPU/RAM, network and battery behavior.
12. Add Test Center/CI coverage and promote only after gates pass.

## 19. Definition of Done

EYES OF PLAYAI v1.0 is complete when:

- the Realme can securely connect to its GuardAi session;
- the user can view the live game from the PlayAi visual perspective;
- perception, reasoning and decision overlays are synchronized;
- GuardAi disagreements are visible and auditable;
- mission recommendations expose time/success/confidence/risk;
- failures create structured learning evidence;
- validated strategies can be transferred to NosAi local knowledge;
- measured impact/dependency metrics are available;
- replay/debug data can reconstruct important decisions;
- loss of video cannot compromise the control/safety plane;
- offline NosAi operation remains possible with validated local knowledge.
