"""FastAPI/WebSocket gateway for the NosAi observability dashboard.

Install the optional dashboard extra before running this module:
    pip install -e '.[dashboard]'
    uvicorn app.dashboard.server:app --reload
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from .events import DashboardEvent, DashboardEventBus
from .sources import all_sources, image_reference

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.responses import FileResponse
except ImportError as exc:  # pragma: no cover - exercised only without optional deps
    raise RuntimeError("Installa l'extra 'dashboard' per avviare NosAi Dashboard") from exc


app = FastAPI(title="NosAi — Centro di controllo", version="1.0")
bus = DashboardEventBus()
WEB_ROOT = Path(__file__).with_name("web")


@app.get("/")
def home() -> FileResponse:
    return FileResponse(WEB_ROOT / "index.html")


@app.get("/api/stato")
def stato() -> dict[str, Any]:
    return {"stato": "pronto", "modalita": "sola osservazione", "connessione": "in attesa"}


@app.get("/api/fonti")
def fonti() -> dict[str, str]:
    return all_sources()


@app.get("/api/immagine-oggetto")
def immagine_oggetto(image_url: str | None = None) -> dict[str, str | None]:
    """Validate an image URL supplied by a data connector before exposing it."""
    return {"image_url": image_reference({"image_url": image_url})}


@app.post("/api/evento")
def pubblica_evento(evento: DashboardEvent) -> dict[str, str]:
    bus.publish(evento)
    return {"stato": "pubblicato"}


@app.websocket("/ws")
async def websocket(websocket: WebSocket) -> None:
    await websocket.accept()
    queue = bus.subscribe()
    try:
        await websocket.send_json({"tipo": "connessione", "stato": "connesso"})
        while True:
            event = await queue.get()
            await websocket.send_json(event.to_dict())
    except WebSocketDisconnect:
        pass
    finally:
        bus.unsubscribe(queue)


async def publish_heartbeat() -> None:
    """Optional heartbeat task for a host runtime."""
    while True:
        bus.publish(DashboardEvent(tipo="heartbeat", dati={"stato": "attivo"}))
        await asyncio.sleep(5)
