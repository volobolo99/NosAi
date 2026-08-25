# NosAi 5.x — piano cronologico

## Fase 0 — Static Data Foundation
1. Contratto unico per dati statici.
2. Manifest, versionamento e checksum delle fonti.
3. Import offline da provider/API approvati in snapshot locali immutabili.
4. Normalizzazione di Items, Monsters/NPC, Skills, BCards, Maps/MapPoints, Quests e localization.
5. Validazione di riferimenti incrociati, duplicati e record corrotti.
6. Generazione di indici ottimizzati per il runtime.
7. Separazione netta tra static data, stato dinamico e memoria appresa.
8. Runtime indipendente dalla rete dopo l'import.
9. Provenance, versione, timestamp e checksum per ogni dataset.

**Regola:** i dati statici non vengono scaricati mentre l'AI gioca. L'import è offline/build-time.

## Fase 1 — Audit tecnico definitivo
File-by-file audit, dipendenze, duplicazioni, error handling, lifecycle, persistenza, test, benchmark e classificazione P0/P1/P2.

## Fase 2 — Consolidamento architetturale
KEEP/MERGE/DEPRECATE/REMOVE, API interne stabili, eliminazione duplicazioni e regression gate.

## Fase 3 — Client Adapter reale
Discovery, preflight, capability detection, state capture, health/heartbeat, reconnect, safe shutdown e diagnostica.

## Fase 4 — Safety Governor
Action validation, confidence gates, stale-state rejection, watchdog, emergency stop e rate limiting.

## Fase 5 — World Model
Player, Entity, Map, Inventory, Skills, Quest, Threats, Objectives, confidence/freshness/source.

## Fase 6 — Perception Engine
Capture, detection, tracking temporale, semantic state e confidence estimation.

## Fase 7 — Decision + Combat Engine
Reactive/hierarchical planning, utility scoring, target/skill selection, cooldown/resource management e replanning.

## Fase 8 — Memory + Learning
Working, episodic e semantic memory; online adaptation controllata; offline learning; decay/versionamento.

## Fase 9 — Self-Diagnostics / Self-Healing
Anomaly detection, fault classification, recovery, post-recovery validation e resume sicuro.

## Fase 10 — Performance adattiva
Hardware budget, scheduler dinamico, adaptive perception frequency, CPU/RAM/GPU e latency budget.

## Fase 11 — Simulation / Digital Twin
Client simulato, world simulator, fault injection, combat/pathfinding scenarios e regression deterministica.

## Fase 12 — Strategy Optimizer
Reward/efficiency/survival/resource objectives, risk-aware optimization e confronto automatico delle strategie.

## Fase 13 — Advanced Pathfinding
Navigation graph, dynamic obstacles, cost/risk maps e learned route quality.

## Fase 14 — Event-driven Runtime + Observability
Event bus, riduzione polling, decision timeline, dashboard e telemetry.

## Fase 15 — Release Gate 5.0
Unit → integration → simulation → stress → fault injection → performance → real-client preflight → safe real-client test → release.

Ogni fase richiede test automatici e baseline misurabile. Nessuna funzionalità avanzata bypassa Safety Governor, World Model o diagnostica.