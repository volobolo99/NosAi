# Gemini Repository Agent — GuardAi / EYES OF PLAYAI v3.0

## Mandato

Agisci come agente di implementazione senior con accesso diretto al repository `volobolo99/NosAi`.

**Modalità autorizzata: WRITE + BRANCH + TEST + PR, senza merge automatico.**

Il tuo compito è ispezionare il codice reale, confrontarlo con la specifica GuardAi / EYES OF PLAYAI v3.0 e produrre/applicare la migliore implementazione possibile. Non ricostruire il progetto da zero e non inventare file già esistenti.

## Regola zero: ispezione prima del codice

Prima di modificare qualsiasi file:

1. identifica branch/ref di lavoro e stato del repository;
2. analizza l'albero completo del repository;
3. individua i moduli Python, C++, Kotlin/Android, Protobuf, Docker e GitHub Actions;
4. individua build system e dipendenze;
5. individua i contratti esistenti;
6. individua eventuali componenti GuardAi già implementati;
7. individua test esistenti;
8. confronta il codice con tutta la documentazione architetturale disponibile;
9. classifica ogni componente:
   - `EXISTS_AND_COMPATIBLE`
   - `EXISTS_NEEDS_MODIFICATION`
   - `MISSING`
   - `CONFLICTING`
   - `DEPRECATED`
10. crea quindi un piano di implementazione prima di applicare modifiche.

**Non generare codice sulla base di supposizioni se il repository può essere ispezionato.**

## Fonte di verità

Usa prioritariamente i documenti e i contratti già presenti nel repository e la specifica GuardAi v3.0 fornita al progetto.

In caso di conflitto:
- segnala il conflitto;
- identifica le fonti coinvolte;
- non cambiare silenziosamente un contratto;
- privilegia la fonte architetturale più autorevole già stabilita dal progetto.

## Obiettivo tecnico

Implementare/completare:

**GuardAi / EYES OF PLAYAI v3.0**

PC Windows Host:
- NosAi / PlayAI operativo;
- GPU NVIDIA;
- DXGI Desktop Duplication o adapter già approvato;
- NVENC;
- WebRTC;
- Protobuf;
- DuckDB locale.

Android Realme X50 Pro:
- cabina tattica GuardAi;
- WebRTC hardware rendering;
- MediaCodec;
- SurfaceView/SurfaceViewRenderer;
- overlay trasparente;
- Room + SQLite WAL;
- Human-in-the-Loop.

## Vincoli assoluti

1. Nessun cloud nel video realtime.
2. Supabase non deve essere usato per streaming o scritture telemetry ad alta frequenza.
3. Separare Video Plane, Telemetry Plane, Control Plane, Storage Plane e Signaling/Pairing Plane.
4. Mantenere isolamento di rete e capability boundaries esistenti.
5. Non introdurre un nuovo trasporto per azioni di gioco.
6. Android non deve poter eseguire arbitrariamente comandi sul PC.
7. Fail-closed in caso di pairing/capability/security failure.
8. Evitare copie RAM inutili.
9. Non dichiarare zero-copy senza dimostrazione tecnica.
10. Non dichiarare <15 ms senza benchmark hardware reale.
11. Non rompere contratti esistenti.
12. Non fare merge automatico.

## Pipeline video richiesta

```text
DXGI
  -> GPU texture
  -> NVENC
  -> WebRTC video track
  -> network
  -> WebRTC receiver
  -> MediaCodec / hardware decoder
  -> SurfaceViewRenderer
  -> transparent tactical overlay
```

Target architetturale:
- 1920x1080;
- 60 FPS;
- CBR circa 15 Mbps;
- B-frames disabilitati;
- bassa latenza;
- percorso hardware;
- target end-to-end <15 ms.

Per ogni passaggio documenta ownership, memoria, eventuale copia, sincronizzazione GPU/CPU e lifetime.

## PTS Sync

Usa `presentation_timestamp_us` come riferimento temporale primario.

Correla frame e telemetry tramite:
- `frame_id`;
- `presentation_timestamp_us`.

Implementa un `PtsSynchronizer` con:
- tolerance window configurabile;
- exact match;
- skew calculation;
- stale detection;
- missing frame handling;
- reorder;
- duplicate handling;
- metrics.

Formula:

```text
pts_skew_us = abs(video_pts_us - telemetry_pts_us)
```

## Telemetry

Usa Protobuf su WebRTC DataChannel unordered/unreliable, privilegiando freshness rispetto a retransmission di dati vecchi.

Implementa:
- producer;
- serializer;
- sender;
- receiver;
- validator;
- decoder;
- stale/drop policy;
- backpressure;
- metrics.

## Pairing e signaling

Device:
`REALME_X50_PRO_GUARD`

Role:
`REALME_CLIENT`

Implementa e/o preserva la state machine:

```text
DISCONNECTED
 -> CONNECTING
 -> PAIRING
 -> APPROVED
 -> NEGOTIATING
 -> CONNECTED
 -> OFFLINE
```

Gestisci:
- pairing request;
- approval;
- capability negotiation;
- SDP offer/answer;
- ICE;
- timeout;
- retry limitato;
- reconnect;
- invalid transition;
- fail-closed.

## Human-in-the-Loop

### Manual Recheck

Il touch su Bounding Box deve essere trasformato correttamente tra:
- Android screen;
- view;
- video;
- normalized coordinates.

Gestisci:
- scaling;
- aspect ratio;
- letterboxing;
- rotation;
- crop.

### Mission Utility Score

Swipe orizzontale per:
- `FAST`
- `SMART`
- `DEEP`
- `LOW_RES`

Implementa gesture detector, debounce, state machine, control message, validation, acknowledgement e audit log.

Non trasformare questo canale in un canale di arbitrary game control.

## Android storage

Room + SQLite WAL.

Pipeline:

```text
telemetry
 -> memory queue
 -> batch
 -> Room transaction
```

Flush:
- ogni 60 secondi;
- oppure threshold configurabile;
- flush sicuro allo shutdown.

Gestisci crash, retry, duplicate, transaction e backpressure.

## PC storage

DuckDB locale per Replay Analytics.

Implementa:
- schema;
- batch writer;
- replay;
- session analytics;
- PTS skew analytics;
- telemetry analytics.

## Offline-first

Deve essere definito e testato il comportamento con:
- Internet assente;
- signaling indisponibile;
- LAN disponibile;
- Android disconnesso;
- PC disconnesso;
- database temporaneamente indisponibile.

## Sicurezza

Implementa/verifica:
- authenticated pairing;
- capability allowlist;
- session ID;
- nonce;
- replay protection;
- size limits;
- rate limits;
- malformed packet rejection;
- audit logging;
- fail closed.

## Observability

Aggiungi/verifica metriche per:

```text
video_fps
capture_ms
encode_ms
network_ms
decode_ms
render_ms
e2e_latency_ms
pts_skew_us
telemetry_rate
telemetry_drop_rate
queue_depth
pairing_failures
reconnect_count
manual_recheck_count
mission_mode_changes
gpu_utilization
nvenc_status
decoder_status
```

## Codice: obbligo di completezza

Per ogni file nuovo o modificato:

```text
PATH: <repository-relative-path>
STATUS: NEW | MODIFIED
PURPOSE: <responsabilità>
```

poi il contenuto completo.

Non usare:
- pseudocode;
- ellissi;
- funzioni vuote;
- TODO come sostituto dell'implementazione;
- placeholder non dichiarati.

Se un'API hardware non è disponibile nell'ambiente di sviluppo, crea un adapter reale + mock/test e marca la verifica hardware come `REQUIRES_REAL_HARDWARE_VALIDATION`.

## Linguaggi da privilegiare

Quando richiesto dalla struttura reale, produci codice completo in:

- `.py`
- `.cpp`
- `.h` / `.hpp`
- `.kt`
- `.proto`
- `.yml` / `.yaml`
- Dockerfile / compose
- `.ps1`, `.bat`, `.sh`

Non creare file artificiali solo per aumentare il numero. Ogni file deve avere responsabilità reale.

## Test obbligatori

Implementa test unitari, integration, E2E e fault-injection per:

- PTS;
- Protobuf;
- coordinate;
- gestures;
- state machines;
- queues/backpressure;
- Room;
- DuckDB;
- signaling;
- DataChannel;
- pairing;
- reconnect;
- packet loss;
- reorder;
- duplicate;
- stale data;
- malformed packets;
- encoder unavailable;
- decoder unavailable;
- database failure.

I test devono essere realmente eseguibili.

## CI/CD

Aggiungi/verifica workflow per:
- Python;
- Kotlin/Android;
- C++/CMake;
- Protobuf contracts;
- lint/format;
- security;
- dependency validation;
- Docker;
- integration;
- architecture guards.

Non richiedere una GPU NVIDIA nei job CI standard se l'infrastruttura non la possiede.

## Architecture guards

Creare controlli che impediscano regressioni come:
- Supabase nel realtime hot path;
- cloud streaming;
- arbitrary Android-to-PC command execution;
- telemetria affidabile quando il contratto richiede DataChannel unordered/unreliable;
- B-frames;
- CPU video conversion nel critical path senza motivazione;
- storage sincrono nel realtime path;
- dipendenze circolari.

## Benchmark

Implementa benchmark software automatici e script hardware.

Misura:

```text
capture_ms
encode_ms
transport_ms
decode_ms
render_ms
overlay_ms
telemetry_ms
pts_skew_us
e2e_latency_ms
```

Se non eseguito su hardware reale:

`NOT_RUN`

Mai `PASS`.

## Hardware validation

Genera strumenti per verificare su Windows/NVIDIA:
- GPU;
- driver;
- CUDA/runtime se richiesto;
- NVENC;
- DXGI.

Su Android:
- MediaCodec;
- decoder profile;
- Surface;
- FPS;
- thermal state;
- network.

Produrre report machine-readable quando possibile.

## Workflow di modifica GitHub

1. Crea un branch dedicato:
   `feature/guardai-eyes-v3-gemini-implementation`
2. Applica solo modifiche motivate dall'audit.
3. Preferisci commit atomici e descrittivi.
4. Esegui build/test dopo le modifiche.
5. Correggi gli errori introdotti.
6. Riesegui i gate.
7. Crea una PR.
8. NON fare merge automatico.

## Gate di accettazione

La PR deve riportare chiaramente:

- `IMPLEMENTED`
- `IMPLEMENTED_NOT_VALIDATED`
- `VALIDATED`
- `BLOCKED`
- `REQUIRES_REAL_HARDWARE_VALIDATION`

Per ogni gate indicare:
- comando;
- risultato;
- log sintetico;
- eventuale failure;
- causa;
- fix applicato.

## Criterio fondamentale

Il risultato migliore non è quello con più file, ma quello con **più codice reale utile, integrato con il repository esistente e coperto da test**.

Prima di creare un nuovo file chiediti:

`Esiste già una responsabilità equivalente nel repository?`

Se sì, estendi il componente esistente quando tecnicamente corretto.

## Consegna finale obbligatoria

Alla fine della PR produci un report contenente:

1. Repository audit;
2. Gap analysis;
3. File creati;
4. File modificati;
5. File volutamente non modificati;
6. Contratti preservati;
7. Dipendenze aggiunte;
8. Build eseguiti;
9. Test eseguiti;
10. CI status;
11. benchmark status;
12. hardware validation status;
13. security status;
14. performance status;
15. rischi residui;
16. limiti reali;
17. PR URL;
18. commit list.

## Divieto di falsa validazione

Non dichiarare mai come validato qualcosa che non hai realmente verificato.

In particolare:

- zero-copy reale → richiede verifica tecnica;
- <15 ms end-to-end → richiede benchmark hardware reale;
- NVENC → richiede GPU/driver compatibili;
- MediaCodec → richiede dispositivo Android reale o ambiente equivalente;
- WebRTC E2E → richiede test di integrazione reale.

## RISULTATO DESIDERATO

Trasforma il repository esistente in una implementazione GuardAi / EYES OF PLAYAI v3.0 il più possibile completa, compilabile, testata e pronta per review.

**Non fermarti alla progettazione. Implementa. Testa. Correggi. Verifica. Prepara la PR. Non fare merge.**
