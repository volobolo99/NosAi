"""Package entry point for the safe NosTale client probe.

Usage from a checkout:
    python -m app.client
    python -m app.client --json
"""
from __future__ import annotations

from .live_probe_cli import main


if __name__ == "__main__":
    raise SystemExit(main())
