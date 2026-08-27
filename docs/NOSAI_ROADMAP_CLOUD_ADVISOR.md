# NosAi — Roadmap Extension: Dashboard Cloud Advisor

> **Status:** canonical roadmap extension
> **Date:** 2026-08-27
> **Parent:** `docs/NOSAI_MASTER_ROADMAP.md` + `docs/NOSAI_ROADMAP_CLOUD_COMPUTE_EXTENSION.md`

## Objective

Add a Cloud Compute Advisor to the main NosAi Dashboard. It continuously evaluates the current hardware profile, current workload and current public cloud-provider conditions, then presents three normalized choices:

1. **FREE — Zero-Cost Compute**
2. **ECONOMY — Best Value Compute**
3. **PRO — Maximum Capability**

These are NosAi recommendation tiers, not claims about provider subscription names.

## Architecture

```text
PlayAi ─┐
        ├──> Cloud Advisor <── local benchmark / AutoSet
GuardAi ┘          │
                   ├── periodic provider research
                   ├── current price/quota/capability data
                   ├── workload-fit scoring
                   └── performance/cost forecast
                            │
                 ┌──────────┼──────────┐
                 ↓          ↓          ↓
               FREE      ECONOMY       PRO
                 │          │          │
                 └──────────┼──────────┘
                            ↓
                     User approval
                            ↓
                      Compute Broker
                            ↓
                 validated async result
                            ↓
                        GuardAi/Lab
```

## Roles

### GuardAi
Can request a recommendation when local compute is insufficient or an offline workload would materially benefit from more compute. GuardAi may explain the expected benefit and rank options, but cannot authorize paid usage.

### PlayAi
Can request a recommendation only for non-real-time planning/research workloads. It cannot initiate paid compute or bypass user approval.

### User
Has final authority to connect, enable, disable or pay for a provider.

## Provider research

Implement `CloudResearchService` with provider adapters. Refresh on schedule and on demand. Record `observed_at`, source/reference, plan/provider identifier and confidence.

Collect where publicly available:

- current GPU price;
- GPU class and VRAM;
- CPU/RAM;
- free credits/quota;
- session/interruptibility limits;
- billing granularity;
- regions and estimated latency;
- automation/API support;
- storage costs;
- reliability signals;
- privacy/security/terms constraints.

Never hard-code a permanent winner. Provider data is time-sensitive.

## Initial provider strategy

### FREE
**Primary candidate:** Lightning AI Free. Its current public pricing page advertises a free starting allocation of GPU hours and a free Studio, with limits/restart constraints and availability subject to its current policies. See the official pricing page: https://api.lightning.ai/pricing/

Colab Free and Kaggle remain optional research adapters, not the primary autonomous backend, because free capacity and execution constraints are dynamic.

### ECONOMY
Dynamically compare low-cost options such as RunPod Community Cloud and Vast.ai. RunPod publishes per-second GPU billing and separates Community and Secure Cloud; Vast.ai is marketplace-based and can be cheaper but has more variable host characteristics.

### PRO
Dynamically compare managed/secure providers. RunPod Secure Cloud is the initial candidate; other providers can replace it when current price, capacity, reliability, VRAM and automation data justify that choice.

## Ranking model

```text
CloudScore =
  0.25 workload_fit
+ 0.20 effective_cost
+ 0.15 available_vram
+ 0.15 reliability
+ 0.10 latency/network_fit
+ 0.05 automation_api_quality
+ 0.05 storage_fit
+ 0.05 privacy/security_fit
```

Weights are workload-specific. Long jobs increase reliability/VRAM weight; batch simulation increases cost/throughput weight.

## Dashboard recommendation card

Every proposal should show:

- provider and plan;
- FREE/ECONOMY/PRO tier;
- fit score;
- current estimated cost;
- available GPU/VRAM;
- expected simulation throughput multiplier vs local;
- expected batch throughput;
- estimated latency;
- best workloads;
- limitations;
- privacy/data notes;
- last research timestamp;
- confidence/staleness indicator;
- **Details / Connect / Ignore** controls.

## Performance forecast

Before connection, NosAi calculates the expected impact using the host benchmark and representative workloads.

Metrics:

- GuardAi simulations/minute;
- Monte Carlo rollouts/second;
- MCTS nodes/second;
- prediction batch throughput;
- replay processing time;
- model inference latency;
- practical model/VRAM headroom;
- experiment completion time;
- local GPU/CPU load reduction;
- estimated energy/time saved;
- expected weekly/monthly cost for paid tiers.

Results must be ranges with explicit assumptions. Example multipliers are UI placeholders only; production values must be measured or estimated from current provider capabilities.

## User controls

- Connect / Disconnect;
- cloud enabled/disabled;
- Free-only mode;
- maximum hourly rate;
- maximum GPU-hours;
- weekly/monthly budget;
- approved providers;
- allowed workload classes;
- automatic failover on/off;
- **Never use paid compute**.

No paid provider may be activated solely by PlayAi or GuardAi.

## Safety and privacy

Cloud output is evidence/candidate data only. It cannot directly authorize execution.

Do not send live credentials, secrets or unnecessary personal/live-game data. Cloud jobs require version, scenario, model, profile, seed, input/output hashes, provider metadata, timestamp and validation status.

Real-time workloads remain local:

- perception-to-decision loop;
- World Model updates required for immediate action;
- Decision Fabric;
- Safety Gate;
- Human Override;
- hard-deadline GuardAi review;
- final execution authorization.

## New phases

### Phase 15A — Dashboard Cloud Advisor — TODO
Provider research, three recommendation tiers, scoring, forecast, explanation, user controls and provenance/staleness indicators.

**Exit:** user can understand three current cloud choices and their expected impact before connecting any provider.

### Phase 19A — Compute Broker — TODO
Provider adapters, asynchronous jobs, quota management, provenance, validation and local fallback.

### Phase 20A — Hybrid Offline Arena — TODO
Distribute large L2/L3 workloads to approved cloud providers while preserving reproducibility.

## Validation gates

- Three tiers generated when eligible data exists;
- provider source and timestamp recorded;
- stale data visibly marked;
- forecast is benchmark-derived;
- costs include assumptions;
- paid connection requires explicit user approval;
- cloud outage does not block real-time NosAi;
- corrupt/untrusted cloud output is rejected;
- cloud output cannot bypass Decision Fabric/Safety Gate;
- recommendation can be explained and replayed.

## Non-negotiable rule

**The cloud improves NosAi; it must never become a hidden dependency for safe real-time operation.**
