# GuardAi / EYES OF PLAYAI v3.0 — Audit + Implementation Report

## Execution mode

`WRITE + BRANCH + TEST + PR`

Merge automatico: **NO**.

Repository: `volobolo99/NosAi`
Branch: `feature/guardai-eyes-v3`
Base: `develop/nosai-next`
PR: #105

## Audit iniziale

La PR #105 risultava aperta e mergeable, con 26 file modificati, 1,288 aggiunte e 30 commit. La PR dichiarava già implementati Protobuf, DXGI/NVENC profile, signaling, WebRTC telemetry, overlay PTS, HITL, DuckDB, Room WAL, Docker e regression tests. Tuttavia la validazione hardware (<15 ms, zero-copy reale e PTS skew E2E) era correttamente non dichiarata come PASS.

### Findings principali

### F1 — Control plane non implementato realmente

`GuardAiActivity.kt` conteneva `sendCommand(...)` come boundary vuoto/commentato. Manual Recheck e MissionSolverMode quindi non avevano un trasporto concreto.

**Stato:** FIXED

### F2 — PTS matching troppo rigido

L'overlay utilizzava lookup esatto `telemetryBuffer[currentVideoPTS]`. Con un trasporto realtime è possibile avere piccoli delta di timestamp; la specifica richiede correlazione temporale, non un'assunzione di uguaglianza perfetta.

**Stato:** FIXED

È stato introdotto matching nearest-PTS con tolerance window di 5 ms, mantenendo il PTS come chiave primaria e rifiutando dati oltre finestra.

### F3 — Swipe mode wrap-around

La formula precedente per il decremento aveva una precedenza operatoria ambigua e poteva produrre un indice errato per il percorso backward.

**Stato:** FIXED

### F4 — Signaling URL localhost hardcoded

Il fallback Android a `wss://127.0.0.1:8888/ws/signaling` non rappresentava il PC Host remoto e poteva mascherare una configurazione mancante.

**Stato:** FIXED

Ora l'assenza di `SIGNALING_URL` porta a modalità offline con messaggio esplicito invece di tentare un endpoint localhost implicito.

## Implementazione applicata

### Control protobuf

Aggiunto:

`android_client/app/src/main/proto/control.proto`

Contratti:
- ManualRecheck
- MissionSolverMode
- MissionModeChange
- ControlCommand

### Android Control DataChannel

`GuardAiActivity.kt` ora serializza `ControlCommand` e invia il payload binario sul DataChannel `guardai-control` esclusivamente quando il canale è OPEN.

Sono separati:
- `guardai-control`
- telemetry DataChannel

### PTS

Aggiunto matching nearest-PTS bounded a 5 ms nell'overlay.

### Storage

La pipeline Room WAL + batch asincrono esistente viene preservata.

### Sicurezza/isolation

Non è stato introdotto alcun trasporto cloud o nuovo canale per arbitrary game actions.

## File modificati in questo passaggio

1. `android_client/app/src/main/java/com/playai/guardai/telemetry/ui/GuardAiActivity.kt`
2. `android_client/app/src/main/java/com/playai/guardai/telemetry/ui/TelemetryOverlayView.kt`
3. `android_client/app/src/main/java/com/playai/guardai/telemetry/ui/TelemetryOverlayViewWithGesture.kt`

## File nuovi

1. `android_client/app/src/main/proto/control.proto`
2. `docs/guardai/GUARDAI_V3_GEMINI_AUDIT_IMPLEMENTATION_REPORT.md`

## Validation status

`IMPLEMENTED_NOT_VALIDATED`

### Non eseguito dal connector

- Android Gradle build
- C++/DXGI build
- GPU/NVENC hardware test
- Realme X50 Pro MediaCodec test
- WebRTC E2E
- <15 ms end-to-end benchmark
- zero-copy hardware proof

L'ultimo SHA della branch è:

`865c238a2845d856757bdb7d208dffad114f7720`

Non risultano workflow GitHub Actions associati a questo SHA tramite l'endpoint disponibile; pertanto CI è `NOT_RUN`, non PASS.

## Gate da eseguire sul runner/hardware

1. Android `assembleDebug` + unit tests + lint.
2. Protobuf generation/contract tests.
3. Host Python tests.
4. Native C++ build.
5. Docker NVIDIA validation.
6. Signaling integration test.
7. WebRTC LAN E2E.
8. PTS skew benchmark.
9. Realme X50 Pro MediaCodec/render validation.
10. Windows NVIDIA DXGI/NVENC latency benchmark.
11. Full end-to-end latency measurement.

## Decisione

La PR resta **aperta e non mergiata** fino alla verifica dei gate. Le modifiche di questo audit correggono due punti di integrazione reali e rendono il Control Plane concreto senza alterare il contratto telemetry esistente.
