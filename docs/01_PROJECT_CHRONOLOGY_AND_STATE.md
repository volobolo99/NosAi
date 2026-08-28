# NosAi — Project Chronology and Technical State

**Document:** `docs/01_PROJECT_CHRONOLOGY_AND_STATE.md`  
**Branch inspected:** `develop/nosai-next`  
**Baseline version:** `4.21.0`  
**Release label:** `full-runtime-fusion-hardened`  
**Stable branch:** `main` (`4.19.2`)  
**Purpose:** chronological and technical baseline for subsequent implementation work.

> **Evidence rule.** This document records what is supported by the repository. Where the repository does not expose enough evidence to reconstruct an exact historical sequence, the item is marked as such rather than inferred as fact. Maturity percentages are engineering estimates from the repository README, not proof of real-world validation.

---

## 1. Storico e Cronologia del Codice

### 1.1 Timeline verificabile

| Versione / fase | Evidenza repository | Funzionalità / evoluzione |
|---|---|---|
| **4.19.2** | `CHANGELOG.md`, `README.md` | Fondazione/migrazione del repository: configurazione Python, ignore rules, guida di sviluppo, CI foundation e preservazione dell'archivio runtime come baseline. Nessun cambio runtime intenzionale dichiarato. |
| **4.20.0** | `CHANGELOG.md` | Introduzione del modello strategico NosTale source-grounded: `NosTaleState`, obiettivi stanza, segnali di resistenza/Dignity, hardcore raid e provenance dei reward. |
| **4.21.0** | `CHANGELOG.md`, `version.json` | Introduzione del `NosAiBrain`, scoring safety-first/objective-aware, confidence/risk/urgency, memoria episodica bounded, replay JSONL, `BrainPipeline`, regression test e capability opzionali RL/vision. |
| **Stato attuale** | `README.md` su `develop/nosai-next` | Evoluzione verso runtime offline-first/continually improving, governance candidate/evidence, sandbox→replay→regression, dashboard/observability, progression e client observation boundary. |

La cronologia completa commit-by-commit non è riprodotta qui quando i metadati disponibili non permettono di attribuire in modo affidabile ogni singolo cambiamento a una funzionalità. La cronologia sopra usa il `CHANGELOG.md` come fonte primaria per le milestone funzionali.

### 1.2 Evoluzione architetturale

Il progetto è evoluto attraverso questi paradigmi:

1. **Repository foundation (4.19.2)** — struttura source-first e riproducibile, con `app/` come runtime e `tests/` come suite.
2. **Strategic domain layer (4.20.0)** — le ipotesi strategiche vengono espresse in modelli e segnali ispezionabili invece di essere nascoste in una policy neurale.
3. **Brain + learning substrate (4.21.0)** — decision scoring, memoria, replay e pipeline sono separati dal boundary di controllo del client.
4. **Offline-first evolution** — ricerca/esperienza produce candidati isolati che passano attraverso sandbox, replay, regression, anti-forgetting e staging prima della consolidazione.
5. **Real-client observation boundary** — il client Windows è esposto tramite un `ClientAdapter` esplicito; `WindowsNosTaleAdapter` è observation-only durante la validazione della percezione.
6. **Governance/release gates** — `main` è stabile e solo convalidato; `develop/nosai-next` è il candidato di integrazione; la promozione richiede gate e conferma esplicita.

Il README della branch di sviluppo descrive inoltre una pipeline architetturale formale:

```text
real experience
  -> observation
  -> online research
  -> candidate
  -> sandbox
  -> replay
  -> regression
  -> anti-forgetting
  -> offline staging
  -> real Windows
  -> real NosTale
  -> explicit confirmation
  -> consolidation
```

---

## 2. Mappatura Attuale del Repository

### 2.1 Albero logico delle directory

Il repository è source-first: `app/` contiene il runtime e `tests/` la validazione. La struttura sotto riassume le aree individuate direttamente nel repository; i file non pertinenti sono omessi dal diagramma per leggibilità.

```text
NosAi/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── quality.yml
│   │   ├── hardware-benchmark.yml
│   │   ├── test-center-144.yml
│   │   ├── security-test-center.yml
│   │   ├── windows-runtime.yml
│   │   ├── runtime-profile.yml
│   │   ├── build-launcher.yml
│   │   ├── python-compatibility.yml
│   │   ├── dependency-review.yml
│   │   ├── action-sha-audit.yml
│   │   ├── bandit.yml
│   │   ├── codeql.yml
│   │   ├── codacy.yml
│   │   ├── sonarcloud.yml
│   │   ├── fortify.yml
│   │   ├── black-duck-security-scan-ci.yml
│   │   ├── frogbot-scan-and-fix.yml
│   │   ├── apisec-scan.yml
│   │   ├── pyre.yml
│   │   ├── nightly-maintenance.yml
│   │   └── release.yml
│   ├── CODEOWNERS
│   ├── dependabot.yml
│   └── pull_request_template.md
├── .nosai/
│   └── test-center/
├── app/
│   ├── ai/
│   │   ├── brain.py
│   │   ├── brain_pipeline.py
│   │   └── live_bridge.py
│   ├── ai_lab/
│   │   ├── runner.py
│   │   └── matrix.py
│   ├── client/
│   │   ├── live_probe_cli.py
│   │   ├── live_observation.py
│   │   ├── nostale_windows.py
│   │   └── windows_perception.py
│   ├── dashboard/
│   │   ├── server.py
│   │   ├── events.py
│   │   ├── observability.py
│   │   ├── sources.py
│   │   └── web/
│   ├── diagnostics/
│   ├── knowledge/
│   ├── nostale/
│   │   └── strategy.py
│   ├── progression/
│   │   ├── advisor.py
│   │   ├── bridge.py
│   │   └── decision_gate.py
│   ├── simulation_repair.py
│   └── preflight.py
├── docs/
│   ├── NOSAI_PROJECT_ARCHITECTURE.md
│   ├── NOSAI_MASTER_ROADMAP*.md
│   ├── AI_BRAIN_ARCHITECTURE.md
│   ├── OPTIMIZATION_7_SYSTEMS.md
│   ├── ARCHITECTURE_HARDENING_GATE.md
│   ├── NOSAI_GATE_PLAYAI_GUARDAI_INTEGRATION.md
│   ├── NOSAI_GATE_E2E_VERIFICATION.md
│   ├── BRANCHING_AND_RELEASE_POLICY.md
│   ├── WINDOWS_SANDBOX_REPLAY_REGRESSION.md
│   ├── P0_EVOLUTION_GATES.md
│   └── other architecture/research/validation documents
├── tests/
│   ├── integration/
│   ├── test_brain.py
│   ├── test_brain_memory_advisory.py
│   ├── test_memory_ab.py
│   ├── test_playai_guardai_bridge.py
│   ├── test_progression_advisor.py
│   └── other unit/regression tests
├── pyproject.toml
├── version.json
├── CHANGELOG.md
├── README.md
├── SECURITY.md
└── CONTRIBUTING.md
```

### 2.2 Responsabilità principali

- **`app/ai/`** — cervello decisionale, pipeline di dominio e bridge verso runtime/live boundary.
- **`app/ai_lab/`** — laboratorio di valutazione/sperimentazione offline e matrici di scenari.
- **`app/client/`** — boundary del client reale, preflight, osservazione e percezione Windows.
- **`app/dashboard/`** — gateway FastAPI/WebSocket e centro di controllo/observability.
- **`app/nostale/`** — rappresentazione strategica NosTale source-grounded.
- **`app/progression/`** — advisor, bridge e gate di decisione per la progressione.
- **`tests/`** — unit, regression e integration validation.
- **`.github/workflows/`** — CI, quality, security, Test Center, runtime e hardware benchmark gates.
- **`docs/`** — specifiche, roadmap, governance, architettura e procedure di validazione.

### 2.3 Stack tecnologico e dipendenze

**Python**

- Versione minima: `>=3.10`.
- Build: `setuptools>=83.0.0`, `wheel`.
- Test: `pytest>=9.0.3,<10`, `pytest-cov>=6,<7`.
- Lint: `ruff>=0.6,<1`.
- ML opzionale: `torch>=2.0`.
- RL opzionale: `gymnasium>=1.0,<2`, `stable-baselines3>=2.6,<3`.
- Vision opzionale: `mss>=10,<11`, `opencv-python>=4.10,<5`.
- OCR opzionale: `pytesseract>=0.3.13,<1`.
- Dashboard: `fastapi>=0.115,<1`, `uvicorn[standard]>=0.30,<1`.
- Test HTTP: `httpx>=0.27,<1`.
- Numerics: `numpy>=1.26,<3`.

Le versioni sopra sono quelle dichiarate in `pyproject.toml`; non costituiscono prova che ogni optional extra sia installato nell'ambiente corrente.

**CI/CD e sicurezza**

Sono presenti workflow per CI, quality, Python compatibility, Test Center, hardware benchmark, Windows runtime, release, CodeQL, Bandit, dependency review, Codacy, SonarCloud, Fortify, Black Duck, Frogbot, API security e altri controlli.

**Configurazione**

`pyproject.toml` è la fonte di verità per build/package/versione Python; `version.json` e metadata README devono essere allineati. La branch `develop/nosai-next` dichiara `4.21.0`; `main` è la baseline stabile `4.19.2`.

---

## 3. Matrice di Stato dei Moduli

> **Nota:** “completato” qui significa implementato nel repository con test/evidence compatibili con la superficie osservata; non significa automaticamente validazione hardware o validazione live-client.

| Modulo | Stato | Evidenza / limite |
|---|---|---|
| Repository/release structure | **COMPLETATO** | Baseline, branching e version governance presenti. |
| Python package/build | **COMPLETATO** | `pyproject.toml` definisce build, package, extras e CLI. |
| NosTale strategy model | **COMPLETATO / VALIDAZIONE DOMINIO PENDING** | Modello esplicito e regression test; le meccaniche source-derived restano ipotesi fino a osservazione live/autorità. |
| NosAiBrain | **IMPLEMENTATO** | Brain, scoring, confidence/risk/urgency e decision reasons presenti. |
| Episodic memory | **IMPLEMENTATO** | Memoria bounded e test associati. |
| JSONL replay | **IMPLEMENTATO** | Persistenza replay offline dichiarata nel changelog. |
| BrainPipeline | **IMPLEMENTATO** | Bridge tra domain state e brain, separato dal client control boundary. |
| RL capability | **IN PROGRESS** | Dipendenze opzionali presenti; README stima RL layer 45%. |
| Vision capability | **IN PROGRESS** | MSS/OpenCV opzionali; percezione Windows presente, validazione reale pending. |
| Real Windows observation adapter | **IMPLEMENTATO_NOT_VALIDATED** | `WindowsNosTaleAdapter`, observation-only; live host validation richiesta. |
| Live preflight | **IMPLEMENTATO** | Controlli Python/deps/import/client/state/action-validation non distruttiva. |
| Dashboard | **IMPLEMENTATO** | FastAPI + WebSocket, pagine e API di observability presenti. |
| Progression advisor/gates | **IMPLEMENTATO** | Advisor, bridge e decision gate presenti con test. |
| Sandbox/replay/regression governance | **IN PROGRESS** | Pipeline e contratti presenti; README indica maturità 45% e host validation pending. |
| Windows Sandbox backend | **IN PROGRESS** | Backend presente ma fail-closed fino a validazione su host Windows supportato. |
| Unified observability | **IN PROGRESS** | Dashboard/evidence presenti; README stima 45%. |
| Model/strategy registry | **IN PROGRESS** | Contratto/local store presenti; README stima 60%. |
| Local inference | **IN PROGRESS** | README stima 30%. |
| Continual learning / anti-forgetting | **IN PROGRESS** | Gate/evidence presenti; training loop pending, README 65%. |
| Real Windows runtime | **IN PROGRESS** | README 25%. |
| Real NosTale client | **EARLY / IN PROGRESS** | README 15%; adapter observation-only. |
| Real action transport | **INTENZIONALMENTE GATED** | README 5%; non è una lacuna accidentale ma una safety boundary. |
| Autonomous evolution loop | **IN PROGRESS** | README 25%. |
| GuardAi/EYES v3 PC↔Android hardware path | **MANCANTE / DA VALIDARE** | Il repository baseline esaminato non dimostra una pipeline hardware end-to-end DXGI→NVENC→WebRTC→MediaCodec→SurfaceView su PC/Realme reale. |
| GuardAi <15 ms E2E | **NON VALIDATO** | Richiede benchmark hardware reale. |
| Zero-copy fisico | **NON VALIDATO** | Richiede profiling della memoria/GPU reale. |
| PTS skew end-to-end hardware | **NON VALIDATO** | Richiede test PC↔Android reali. |

### 3.1 Maturity baseline dichiarata dal repository

La branch `develop/nosai-next` dichiara queste stime, che vengono riportate senza trasformarle in test passati:

```text
Repository/release structure          95%
Test/evidence foundation              80%
Research -> candidate -> simulation   70%
Promotion/evolution governance       70%
Protected replay                      70%
Candidate regression                  55%
Sandbox -> replay -> regression       45% (host validation pending)
Windows Sandbox backend               35% (host validation pending)
Offline-first AI core                 55%
RL layer                              45%
Memory/retrieval                      40%
Local inference                       30%
Continual learning / anti-forgetting  65% (training loop pending)
Unified observability                 45%
Model/strategy registry               60%
Real Windows runtime                  25%
Real NosTale client                   15%
Real action transport                  5% (intentionally gated)
Autonomous evolution loop             25%
```

---

## 4. Contratti e API Esistenti

### 4.1 CLI/package entry points

`pyproject.toml` espone:

```text
nosai-preflight       -> app.preflight:main
nosai-pilot           -> app.pilot.cli:main
nosai-pilot-cycle     -> app.pilot.cli:main
nosai-client-probe    -> app.client.live_probe_cli:main
nosai-diagnostics     -> app.diagnostics.cli:main
nosai-dashboard       -> app.dashboard.cli:main
nosai-knowledge-import -> app.knowledge.importers.cli:main
```

### 4.2 Dashboard HTTP API

`app/dashboard/server.py` definisce il gateway FastAPI e i seguenti endpoint osservabili:

```text
GET  /                       -> control_center.html
GET  /control-center         -> control_center.html
GET  /runtime                -> runtime.html
GET  /game-view              -> game_view.html
GET  /diagnostics            -> diagnostics.html
GET  /sources                -> sources.html
GET  /test-center            -> test_center.html
GET  /ai-lab                 -> ai_lab.html
GET  /simulation             -> simulation.html

GET  /api/test-center        -> dict[str, Any]
GET  /api/ai-lab             -> dict[str, Any]
GET  /api/simulation         -> dict[str, Any]
GET  /api/stato              -> dict[str, Any]
GET  /api/live-observation   -> dict[str, Any]
GET  /api/perception         -> dict[str, Any]
GET  /api/screenshot         -> PNG StreamingResponse
GET  /api/fonti              -> dict[str, str]
GET  /api/immagine-oggetto   -> dict[str, str | None]
POST /api/evento             -> dict[str, str]
WS   /ws                     -> dashboard event stream
```

Il dashboard contiene anche `set_runtime_adapter(adapter)` e `configure_nostale_observation()` come boundary di configurazione dell'adapter.

### 4.3 Client adapter contract

Il repository stabilisce che una integrazione live deve fornire un `ClientAdapter` esplicito configurato come `module:attribute` tramite `NOSAI_CLIENT_ADAPTER` o `--client-adapter`.

`WindowsNosTaleAdapter` costituisce il boundary concreto per il client Windows e, nello stato documentato, è **observation-only**: non esegue input, patching di memoria, action transport o game actions.

### 4.4 State / perception contracts

Il dashboard usa funzioni di dominio come:

```text
snapshot_from_adapter(adapter) -> snapshot.to_dict()
LiveObservation(adapter).capture() -> (world, metadata)
WindowsNosTalePerception(adapter).capture() -> frame
```

Il frame di percezione espone almeno le proprietà usate dal server:

```text
width
height
source
observation_only
png
```

### 4.5 Dashboard event contract

`POST /api/evento` riceve un `DashboardEvent` e lo pubblica su `DashboardEventBus`. Il WebSocket `/ws` invia inizialmente un evento di connessione e successivamente serializza gli eventi con `event.to_dict()`.

### 4.6 AI Lab contract

`GET /api/ai-lab` restituisce un payload strutturato con:

```text
status
mode = offline-deterministic
external_provider = NOT_REQUIRED
scenarios
candidates
results { PASS, FAIL, NOT_RUN }
metrics { accuracy_percent, safety_violation_percent, p50_latency_ms, p95_latency_ms }
scenario_errors
evidence
```

### 4.7 Simulation contract

`GET /api/simulation` restituisce lo snapshot di `SimulationRepairEngine` e non deve mutare il source tree.

### 4.8 Test Center / evidence contract

`GET /api/test-center` integra `scan_repository()` con `load_ci_evidence()` e mappa almeno:

```text
G3 <- junit.status
G6 <- coverage.status
security <- CI security evidence
sbom <- SBOM evidence
```

### 4.9 Strategy / brain contracts

Il modello NosTale espone uno stato strategico esplicito (`NosTaleState`) e il brain usa gli input di dominio per scoring orientato a sicurezza/obiettivo. Il changelog stabilisce inoltre confidence, risk, urgency, decision reasons, episodic memory e replay metadata.

La firma completa di ogni classe/metodo non è ricostruita in questa baseline quando non è stata estratta direttamente dal file sorgente: il documento evita di inventare firme non osservate.

---

## 5. Baseline per il Codice Successivo

Prima di implementare nuovi moduli, l'agente deve assumere come invarianti:

1. `main` è la baseline stabile `4.19.2`.
2. `develop/nosai-next` è la baseline di integrazione `4.21.0`.
3. `pyproject.toml` è la fonte di verità per package/build/versione Python.
4. Le strategie NosTale source-derived sono ipotesi verificabili, non verità hard-coded non dimostrate.
5. Il live client boundary resta esplicito e observation-only finché la validazione non autorizza ulteriori capacità.
6. Il core deve rimanere offline-first.
7. La promozione richiede test, evidence, sicurezza, runtime validation quando applicabile e conferma esplicita.
8. Non deve essere dichiarato `PASS` ciò che non è stato realmente eseguito.
9. Per GuardAi hardware, <15 ms, zero-copy e PTS E2E devono restare `NOT_VALIDATED` finché non esistono misure sul target reale.
10. Le nuove modifiche devono essere piccole, tracciabili, testate e compatibili con i contratti esistenti.

## 6. Fonti Repository Consultate

- `README.md`
- `CHANGELOG.md`
- `pyproject.toml`
- `version.json`
- `docs/BRANCHING_AND_RELEASE_POLICY.md`
- struttura `.github/workflows/`
- `app/dashboard/server.py`
- `app/ai/brain.py`
- `app/ai/brain_pipeline.py`
- `app/ai/live_bridge.py`
- `app/nostale/strategy.py`
- `app/progression/*`
- `app/client/*`
- test brain/memory/progression/GuardAi e integration test individuati nel repository
- documentazione GuardAi, architettura, hardening ed E2E presente in `docs/`

---

**Baseline status:** `DOCUMENTED`  
**Runtime validation status:** `PARTIAL / CONTEXT-DEPENDENT`  
**GuardAi hardware validation:** `REQUIRES_REAL_HARDWARE_VALIDATION`  
**Release promotion:** `NOT_AUTHORIZED_BY_THIS_DOCUMENT`
