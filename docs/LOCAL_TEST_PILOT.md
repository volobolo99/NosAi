# NosAi Local Test Pilot

The first PC version is intentionally **non-live**. It collects local runtime data,
scenario telemetry, errors, performance context, and durable learning records.
It never authorizes live game actions.

## Windows quick start

From the repository root in PowerShell:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest
python -m app.preflight
python -m app.pilot.cli --cycle --ticks 500
```

Equivalent installed command:

```powershell
nosai-pilot-cycle --cycle --ticks 500
```

## Outputs

The command writes to `artifacts/pilot/`:

- `system_profile.json` — portable CPU/OS/Python runtime characteristics;
- `<scenario>.jsonl` — append-only telemetry;
- `<scenario>.report.json` — machine-readable report;
- `<scenario>.report.html` — human-readable report;
- `learning_ledger.json` — durable error knowledge across sessions;
- `repair_queue.json` — deterministic repair tasks for a future repair agent.

These artifacts are the first local dataset. They should be retained between runs.

## Closed-loop design

```text
run safe scenarios
      -> telemetry
      -> JSON + HTML reports
      -> error aggregation
      -> learning ledger
      -> repair queue
      -> future repair agent
      -> regression test
      -> proposed patch
      -> CI/test gates
      -> reviewed application
```

The learning ledger is deliberately separate from source code. A failed or
malformed telemetry record must never be able to overwrite the application.
A future repair agent can consume `repair_queue.json`, generate a patch and add
a regression test; the normal test/CI gates remain mandatory before source changes
are accepted.

## Modes

- `simulation`: deterministic local adapter; no game client.
- `shadow`: architecture slot for observing a future client adapter without action execution.
- `dry_run`: validation-only architecture slot; live execution remains disabled.

The current Test Pilot always reports `ready_for_live_action: false`.

## First real-PC objective

Run at least three scenarios and preserve the artifacts. The next engineering
step is to analyze the resulting latency/error/capability data, then design the
real `ClientAdapter` around observed requirements rather than guesses.
