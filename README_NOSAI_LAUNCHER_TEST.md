# Nos AI Launcher Test

## Uso

1. Avvia `scripts/Avvia_NosAi_Scanner.bat` oppure il build Windows `Nos AI Launcher Test.exe`.
2. Seleziona **solo** la cartella principale del client NosTale.
3. Premi **AVVIA TEST COMPLETO**.
4. Al termine trovi in `artifacts/`:
   - `client-manifest.json`
   - `nosai-client-test-report.json`
   - `nosai-client-test-report.sanitized.json`
   - `nosai-diagnostic-package.zip`

## Condivisione

Il pacchetto ZIP è progettato per essere caricato manualmente su GitHub dopo la verifica. Non include automaticamente gli asset proprietari `.NOS`.

## Build EXE

Il workflow `Build Nos AI Launcher Test` crea automaticamente un EXE Windows portable tramite GitHub Actions. Il risultato è disponibile come artifact della workflow.

## Privacy

Il sanitizer rimuove campi sensibili comuni e sostituisce i nomi utente presenti nei percorsi Windows/Linux. Prima della pubblicazione è comunque consigliata una verifica del report.
