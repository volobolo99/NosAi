"""Windows-friendly manual selection of a NosTale client directory."""
from __future__ import annotations

import os
from pathlib import Path


def select_client_path() -> str:
    """Open a native folder picker and return the selected absolute path.

    The picker is intentionally explicit: NosAi never scans the whole disk or
    changes the selected client. A non-Windows environment may still use the
    Tk fallback when available (useful for development/CI).
    """
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError as exc:
        raise RuntimeError("selettore grafico non disponibile; specifica il percorso manualmente") from exc

    root = tk.Tk()
    root.withdraw()
    try:
        root.attributes("-topmost", True)
        selected = filedialog.askdirectory(
            title="Seleziona la cartella del client NosTale",
            mustexist=True,
        )
    finally:
        root.destroy()
    if not selected:
        raise RuntimeError("nessuna cartella NosTale selezionata")
    return os.fspath(Path(selected).expanduser().resolve())
