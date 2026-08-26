"""Command-line entry point for the NosAi observability dashboard."""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Avvia il Centro di controllo NosAi")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("Installa 'pip install -e .[dashboard]' prima di avviare la dashboard") from exc

    uvicorn.run("app.dashboard.server:app", host=args.host, port=args.port, reload=args.reload)
