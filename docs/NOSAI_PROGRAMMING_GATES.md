# NosAi — Ordine di Programmazione a Gate

## Scopo

Questo documento definisce l'ordine ufficiale di sviluppo di NosAi. Il lavoro procede per gate verificabili e non si promuove un gate successivo finché i criteri del gate corrente non sono soddisfatti.

## Regola generale

`Specifica → implementazione → test unitari → integration test → Test Center → CI → benchmark → ottimizzazione → documentazione → gate`

## Gate

### G0 — Fondamenta del progetto
- Struttura repository e moduli.
- Configurazione Windows e gestione configurazione.
- Logging, error handling e diagnostica.
- Lifecycle e separazione `core / runtime / AI / dashboard / tests`.

### G1 — Core funzionante
- Componenti fondamentali del core.
- Contratti/interfacce stabili.
- Stato e comunicazione interna verificabili.

### G2 — Runtime funzionante
- Avvio/arresto controllato.
- Event bus.
- Stato globale dell'agente.
- Scheduler.
- Gestione risorse.
- Watchdog e recovery.

### G3 — AI primaria + AI locale secondaria
- AI primaria.
- AI secondaria locale come supporto/fallback.
- Router/orchestratore per la selezione del modello.
- Gestione del contesto e confidence.

### G4 — Memoria + orchestratore
- Memoria di lavoro.
- Memoria persistente/intelligente.
- Context management.
- Pianificazione e coordinamento delle decisioni.

### G5 — Adapter + dry-run/read-only
- Interfacce adapter.
- Adapter simulati/mock.
- Adapter runtime reale come boundary controllato.
- Modalità read-only e dry-run.
- Nessuna azione reale finché i gate precedenti non sono validati.

### G6 — Test Center
- Unit test.
- Integration test.
- End-to-end e regression test.
- Test adapter e AI.
- JUnit/report.
- Coverage.
- Test Center 144.
- Artifact automatici.

### G7 — CI completo
- Lint.
- Static/type checks.
- Test automatici.
- Coverage gate.
- Build e artifact.
- Security/config checks.
- Smoke test.

### G8 — Benchmark + AutoSet
- Rilevamento hardware.
- CPU/RAM/GPU.
- Latenza e throughput.
- Profilazione del carico.
- Selezione automatica dei parametri.
- Profili `safe / balanced / performance`.
- Persistenza della configurazione ottimizzata.

### G9 — Dashboard completa
- Stato NosAi.
- Stato AI primaria/secondaria.
- CPU/RAM/GPU.
- Memoria ed eventi/log.
- Benchmark e AutoSet.
- Test Center, CI e coverage.
- Health checks.
- Configurazione.
- Safe/dry-run.
- Start/stop/restart e diagnostica.

### G10 — Runtime reale controllato
- Collegamento al runtime reale solo dopo i gate precedenti.
- Pre-flight completo.
- Verifica read-only.
- Verifica dry-run.
- Attivazione progressiva e controllata delle capacità consentite.

### G11 — Hardening
- Stress test.
- Fault injection.
- Recovery.
- Crash handling.
- Timeout e concorrenza.
- Persistenza.
- Security/config review.
- Regression completa.

### G12 — Release
- Tutti i gate precedenti verdi.
- Artifact riproducibili.
- Documentazione aggiornata.
- Versione candidata validata.
- Promozione a `main` solo dopo conferma esplicita.

## Stato di avanzamento

Il repository `main` resta la baseline stabile. Lo sviluppo candidato continua nel ramo di sviluppo previsto dal repository e viene promosso solo dopo validazione completa.

Il prossimo lavoro operativo parte da **G0**, senza saltare i gate e mantenendo il principio: prima verificabilità e riproducibilità, poi autonomia, infine ottimizzazione.
