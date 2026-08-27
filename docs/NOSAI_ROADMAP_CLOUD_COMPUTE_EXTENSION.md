# NosAi — Roadmap Extension: Portable + Hybrid Cloud Compute

> **Status:** canonical roadmap extension
> **Date:** 2026-08-27
> **Purpose:** extend the Master Implementation Roadmap with the portable 2 TB SSD runtime, Acer Nitro V16 AI reference profile, hardware-adaptive AutoSet and free-tier cloud offload architecture.

## 1. Decision

NosAi will use a **Hybrid Compute Architecture**:

- the external **2 TB SSD** is the portable NosAi environment and source of truth for portable models, configuration, knowledge, replay/evaluation data, simulator assets and runtime packages;
- the host PC supplies local CPU/GPU/NPU/RAM and OS/client integration;
- a **Compute Broker** may asynchronously offload suitable non-real-time workloads to an approved cloud provider when free capacity is available;
- real-time gameplay-critical reasoning remains local and must not depend on cloud availability.

The cloud is an accelerator, not a runtime dependency.

## 2. Reference hardware profile

The current reference development machine is the user's Acer Nitro V16 AI with:

- AMD Ryzen 7 260;
- NVIDIA GeForce RTX 5060 Laptop GPU;
- 16 GB RAM;
- 180 Hz display.

NosAi should provisionally classify this machine as **HIGH / 16 GB RAM / 8 GB VRAM**, subject to the actual runtime benchmark. The classification must never be hard-coded from the product name.

The benchmark remains authoritative and must measure the real host capabilities, including GPU performance/TGP behavior, CPU throughput, available RAM/VRAM, inference latency, thermal/power behavior where measurable, storage performance and simulation throughput.

## 3. Portable AI Environment

The SSD layout should be logically separated into:

```text
NosAi SSD 2 TB
├── runtime/
├── PlayAi/
├── GuardAi/
├── decision_fabric/
├── world_model/
├── models/
├── knowledge/
├── memory/
├── simulator/
├── replay/
├── benchmarks/
├── profiles/
├── cache/
├── logs/
└── bootstrap/
```

### Portable vs machine-specific boundary

**Portable:** models, application/runtime packages, configuration templates, knowledge, simulator assets, replay/evaluation data and portable memory.

**Machine-specific:** GPU/CPU drivers, OS integration, client adapter dependencies, hardware acceleration libraries and permissions.

The bootstrapper detects the host and binds the portable layer to a generated machine profile rather than modifying the portable source of truth.

## 4. Plug-and-play bootstrap

Target flow:

```text
Connect SSD
    ↓
NosAi Launcher
    ↓
Hardware / OS Discovery
    ↓
Compatibility Check
    ↓
Local Benchmark
    ↓
Capability Profile
    ↓
AutoSet
    ↓
Model + Runtime Selection
    ↓
PlayAi / GuardAi budgets
    ↓
Compute Broker availability check
    ↓
READY / DEGRADED / UNSUPPORTED
```

Profiles are capability-based, not vendor/model-name based:

- HIGH;
- MEDIUM;
- LOW;
- UNSUPPORTED.

Degradation must be graceful and validated. A weak host may reduce model size, concurrency and simulation depth rather than breaking the whole runtime.

## 5. Compute Broker

Add a technology-neutral `ComputeBroker` interface with a provider adapter layer.

Responsibilities:

1. inspect local capacity;
2. classify workload latency sensitivity;
3. decide whether the workload is local-only, cloud-eligible or deferred;
4. check provider availability and free quota;
5. package a reproducible job;
6. submit asynchronously;
7. verify job identity and provenance;
8. retrieve and validate the result;
9. record compute cost/usage and outcome;
10. fall back to local execution or defer when cloud is unavailable.

### Workload classes

**L0 — real-time local-only**
- perception-to-decision loop;
- World Model updates required for immediate action;
- Decision Fabric;
- Safety Gate;
- Human Override;
- hard-deadline GuardAi checks;
- final execution authorization.

**L1 — latency-sensitive local preferred**
- fast GuardAi Critic;
- immediate prediction;
- small tactical simulation;
- short-horizon strategy checks.

**L2 — cloud-eligible asynchronous**
- large batches of counterfactual simulations;
- offline Monte Carlo/MCTS studies;
- replay analysis;
- dataset generation;
- prediction calibration jobs;
- candidate strategy evaluation;
- benchmark matrix runs;
- model evaluation/selection;
- non-production training experiments.

**L3 — deferred/background**
- long-running research experiments;
- large historical replay mining;
- large-scale strategy search;
- candidate model benchmarking.

## 6. Free cloud provider strategy

### Primary candidate: Lightning AI Free

Use Lightning AI as the first provider adapter candidate because its current public pricing/docs advertise a free tier, free GPU credits, GPU Studios and SDK/automation capabilities. The current pricing page states up to 30 free credits to start and describes roughly 80 free GPU hours on interruptible machines, with limits and availability subject to the provider's policies. The documentation also describes free GPU usage and programmatic/IDE workflows.

NosAi must **not assume permanent or guaranteed free capacity**. The provider adapter must treat quota, availability, session lifetime, GPU type and credits as dynamic capabilities.

### Secondary research providers

- Google Colab Free: useful for interactive/offline experiments, but its managed free tier has explicit restrictions and dynamic limits. In particular, the current FAQ states that remote-control/worker-style distributed computing can be restricted on free managed runtimes. Therefore Colab Free must **not** be the primary autonomous Compute Broker backend.
- Kaggle Notebooks: useful for reproducible notebook experiments and free GPU workloads, but quotas/availability change and the service is notebook-oriented. Treat it as an optional research adapter, not a real-time compute backend.

Provider selection must be validated against current Terms/quotas before each implementation milestone.

## 7. Cloud job security and provenance

Never send authoritative live credentials, secrets or unnecessary personal data to a cloud worker.

Cloud jobs must contain:

- immutable job ID;
- NosAi version;
- scenario/simulator version;
- model identifier/version;
- benchmark/profile ID;
- random seed where applicable;
- input dataset hash;
- output hash;
- provider and runtime metadata;
- timestamp;
- resource usage;
- validation status.

Cloud output is **evidence/candidate data**, never direct authorization to execute an action.

All returned results must pass schema, integrity, provenance and plausibility checks before entering GuardAi/Memory.

## 8. Hybrid decision rule

```text
                 Workload
                    ↓
              Compute Broker
                    ↓
        ┌───────────┼───────────┐
        ↓           ↓           ↓
      LOCAL       CLOUD       DEFER
        │           │           │
        │       async job      │
        │           ↓           │
        └─────── validated ─────┘
                    ↓
                 Result
                    ↓
              GuardAi / Lab
```

The broker must optimize for **decision quality per watt/second**, not simply maximum cloud usage.

For every job it should estimate:

`expected_value = expected_quality_gain - latency_penalty - failure_risk`

and use cloud only when the result is useful enough and not required before a hard deadline.

## 9. Free-cloud failure policy

If the free provider is unavailable, quota-exhausted, rate-limited or terminated:

1. do not block real-time PlayAi;
2. do not bypass GuardAi safety requirements;
3. use local reduced-depth computation when safe;
4. defer L2/L3 work;
5. record the reason and provider state;
6. resume queued work when capacity returns.

No provider outage may change the safety policy.

## 10. SSD storage policy

The 2 TB device should use retention classes:

- **CRITICAL:** authoritative configuration, signed/reproducible metadata and essential memory — never auto-delete;
- **IMPORTANT:** replay/evaluation datasets and validated knowledge — long retention;
- **CACHE:** downloaded/intermediate model/runtime artifacts — safely purgeable;
- **EXPERIMENTAL:** cloud outputs, temporary simulations and research artifacts — quota-managed.

A storage manager must prevent simulations, replay and logs from silently consuming the entire SSD.

## 11. Roadmap phase additions

### Phase 12A — Portable AI Environment — TODO
Build the SSD bootstrap/runtime boundary and machine-profile system.

**Exit:** the same SSD can initialize NosAi on a supported host without rewriting portable source data.

### Phase 13A — Hardware Certification Benchmark — TODO
Add a standardized NosAi benchmark suite and generate signed/profiled capability results.

Reference profile:

`NOSAI-HIGH-RTX5060-16GB`

This label is a benchmark result, not a permanent assumption about all Nitro V16 systems.

**Exit:** AutoSet decisions are driven by measured capability.

### Phase 19A — Compute Broker — TODO
Implement workload classification, provider adapters, asynchronous job management, quota awareness, provenance and local fallback.

**Exit:** cloud-eligible workloads can be offloaded without affecting real-time safety or execution.

### Phase 20A — Hybrid Offline Arena — TODO
Allow the Offline Validation Lab to distribute large L2/L3 workloads to approved free compute providers when capacity exists.

**Exit:** offline experiments can scale beyond local hardware while remaining reproducible and auditable.

## 12. New validation gates

**Portable Gate**
- SSD boot/launcher works;
- machine profile generated;
- AutoSet reproducible;
- portable/machine-specific boundary respected.

**Cloud Gate**
- provider unavailable scenario passes;
- quota exhaustion passes;
- timeout/retry passes;
- corrupt result rejected;
- provenance validated;
- no secrets leaked;
- cloud result cannot directly authorize execution.

**Hybrid Gate**
- PlayAi continues when cloud disappears;
- GuardAi hard deadlines remain local;
- L2/L3 work is queued/deferred safely;
- local/cloud result parity is measured where deterministic comparison is possible.

## 13. Updated target architecture

```text
                         NOSAI 2 TB SSD
                              │
                    Portable AI Environment
                              │
                ┌─────────────┴─────────────┐
                │                           │
          Host Machine                Compute Broker
                │                           │
        Hardware Discovery            Provider Adapters
                │                     ┌─────┴─────┐
             Benchmark               │ Lightning │ ...
                │                    │  Free     │
             AutoSet                └───────────┘
                │                           │
        ┌───────┴────────┐                  │ async
        ↓                ↓                  ↓
     PlayAi           GuardAi        Offline Compute
        │                │                  │
        └────────┬───────┘                  │
                 ↓                          │
           Decision Fabric ←──── validated results
                 ↓
            Safety Gate
                 ↓
          Hard Deadline
                 ↓
         Human Override
                 ↓
             Executor
```

## 14. Non-negotiable principle

**NosAi must remain useful without the cloud.**

The cloud exists to increase available compute for offline/asynchronous workloads, reduce local resource pressure and accelerate experimentation. It must never become a hidden dependency for safe real-time operation.
