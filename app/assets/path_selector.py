"""Interactive Windows folder selection for the NosTale client.

The selector is deliberately local-only. It never writes to the selected client
folder; it only returns the directory chosen by the user.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Callable


class ClientPathSelectionError(RuntimeError):
    """Raised when the user cannot select a valid NosTale client directory."""


def validate_client_path(path: str | Path) -> Path:
    candidate = Path(path).expanduser().resolve()
    if not candidate.is_dir():
        raise ClientPathSelectionError(f"Cartella client non trovata: {candidate}")
    return candidate


def select_client_path(initial: str | Path | None = None) -> Path:
    """Open a native folder picker and validate the selected client directory.

    On Windows this uses Tk's native folder dialog. A console fallback is kept
    for headless/test environments, where the caller can provide a path through
    the ``NOSAI_NOSTALE_CLIENT`` environment variable.
    """
    env_path = os.environ.get("NOSAI_NOSTALE_CLIENT")
    if env_path:
        return validate_client_path(env_path)

    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError as exc:
        raise ClientPathSelectionError(
            "Selezione grafica non disponibile: imposta NOSAI_NOSTALE_CLIENT."
        ) from exc

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        selected = filedialog.askdirectory(
            title="Seleziona la cartella del client NosTale",
            initialdir=str(Path(initial).expanduser().resolve()) if initial else None,
            mustexist=True,
        )
    finally:
        root.destroy()

    if not selected:
        raise ClientPathSelectionError("Selezione della cartella annullata")
    return validate_client_path(selected)


def choose_and_scan(
    scanner_factory: Callable[[Path], object],
    initial: str | Path | None = None,
) -> tuple[Path, object]:
    """Select the client directory first, then create the scanner for it."""
    path = select_client_path(initial)
    return path, scanner_factory(path)
