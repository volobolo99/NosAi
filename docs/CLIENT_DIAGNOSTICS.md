# NosAi local diagnostics

`nosai-diagnostics` collects a privacy-safe snapshot used to tune NosAi for the real Windows laptop and NosTale client.

## Commands

```powershell
python -m app.diagnostics.cli --json
python -m app.diagnostics.cli --output artifacts/nosai-diagnostics.json
```

After reinstalling the editable package, the console entry point is also available:

```powershell
nosai-diagnostics --json
```

## Collected

- Windows release/build/architecture and Python runtime.
- Windows computer manufacturer/model.
- CPU name/core counts.
- GPU name/driver/adapter memory as exposed by Windows CIM.
- Total physical memory.
- Configured NosTale process allow-list.
- Whether a visible NosTale window is present.
- PID, title and window rectangle when the client is visible.

## Explicitly not collected

The collector does **not** read passwords, browser data, cookies, access tokens, game memory, packet contents, or account credentials. It does not inject input or perform game actions.

The report schema is `nosai.diagnostics.v1` so later tooling can reject incompatible reports instead of guessing.
