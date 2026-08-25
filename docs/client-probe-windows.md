# Windows client probe

The `nosai-client-probe` console script is installed by pip, but Windows can keep the Python `Scripts` directory outside `PATH`. NosAi therefore also provides a checkout-local launcher that does not depend on the console-script PATH.

From the repository root:

```powershell
python -m app.client
python -m app.client --json
.\tools\nosai-client-probe.cmd --json
```

After changing Python environments, reinstall the editable package:

```powershell
python -m pip install -e ".[dev]"
```

The probe is observation-only. It discovers a running NosTale process/window and reads normalized process/window metadata. It does not inject input, patch memory, or execute game actions.
