# NosAi — Cooperazione IA primaria / IA secondaria locale

## Obiettivo

L'IA secondaria locale è un collaboratore del cervello principale, non un secondo orchestratore indipendente. La primaria mantiene l'autorità decisionale finché non verranno introdotti e validati ulteriori gate di sicurezza e consenso.

## Flusso

```text
Game/Runtime
    ↓
Perception + State
    ↓
Primary Orchestrator
    ├──────────────→ Primary proposal
    │
    └→ Cooperation Router
             ↓
       Local Secondary AI
             ↓
       Secondary proposal
             ↓
       Arbitration Policy
             ↓
       Decision / Safety Gate
             ↓
       Action Executor
```

## Modalità

- **PRIMARY_ONLY** — compiti urgenti, IA locale non disponibile o nessun vantaggio previsto.
- **LOCAL_ASSIST** — la locale fornisce evidenza/valutazione aggiuntiva; la primaria resta autoritativa.
- **DUAL_REVIEW** — compiti ad alto rischio: entrambe producono una proposta e vengono confrontate.
- **LOCAL_FALLBACK** — previsto come estensione successiva quando il runtime locale sarà validato come fallback operativo.

## Regole iniziali

1. Nessuna azione di gioco viene eseguita direttamente dall'IA locale.
2. La primaria resta autoritativa durante la fase di integrazione.
3. Nei task ad alto rischio si richiede revisione duale.
4. In caso di disaccordo, il sistema non considera il consenso implicito: seleziona conservativamente la proposta primaria e segnala che l'esecuzione deve passare dal safety gate.
5. L'AutoSet/benchmark potrà successivamente determinare disponibilità, modello e limiti della locale.
6. La memoria condivisa dovrà passare attraverso un contesto controllato e versionato, evitando che un modello possa alterare direttamente la memoria autorevole.
7. Metriche minime da raccogliere: latenza, disponibilità, confidence, accordo/disaccordo, qualità della proposta e motivazione della selezione.

## Evoluzione prevista

**Gate 1:** contratto di cooperazione (questo modulo).

**Gate 2:** adapter/runtime locale reale.

**Gate 3:** confidence calibration + safety gate.

**Gate 4:** benchmark hardware e selezione automatica del modello.

**Gate 5:** memoria condivisa controllata.

**Gate 6:** modalità fallback locale validata.

**Gate 7:** valutazione online e miglioramento continuo.

Questa separazione permette di sviluppare il cervello locale in seguito senza cambiare il contratto dell'orchestratore principale.
