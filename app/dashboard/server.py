"""FastAPI/WebSocket gateway for the NosAi observability dashboard."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .catalog import ItemCatalog
from .events import DashboardEvent, DashboardEventBus
from .sources import all_sources, image_reference

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.responses import FileResponse
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("Installa l'extra 'dashboard' per avviare NosAi Dashboard") from exc

app = FastAPI(title="NosAi — Centro di controllo", version="1.2")
bus = DashboardEventBus()
WEB_ROOT = Path(__file__).with_name("web")
_runtime_adapter: Any | None = None
_catalog = ItemCatalog()


def set_runtime_adapter(adapter: Any | None) -> None:
    """Attach the observation-only runtime/client adapter."""
    global _runtime_adapter
    _runtime_adapter = adapter


@app.get("/")
def home() -> FileResponse:
    return FileResponse(WEB_ROOT / "index.html")


@app.get("/api/stato")
def stato() -> dict[str, Any]:
    if _runtime_adapter is None:
        return {"stato": "pronto", "modalita": "sola osservazione", "connessione": "in attesa"}
    from .state import snapshot_from_adapter
    return snapshot_from_adapter(_runtime_adapter).to_dict()


@app.get("/api/fonti")
def fonti() -> dict[str, str]:
    return all_sources()


@app.get("/api/oggetto/{item_id}")
def oggetto(item_id: str) -> dict[str, Any]:
    item = _catalog.get(item_id)
    return _catalog.as_dict(item) if item else {"item_id": item_id, "trovato": False}


@app.get("/api/immagine-oggetto")
def immagine_oggetto(image_url: str | None = None) -> dict[str, str | None]:
    return {"image_url": image_reference({"image_url": image_url})}


@app.post("/api/evento")
def pubblica_evento(evento: DashboardEvent) -> dict[str, str]:
    # Gli eventi item/inventario possono portare una fonte NosApki; in tal caso
    # arricchiamo e persistiamo automaticamente prima della trasmissione LIVE.
    if evento.tipo in {"item_rilevato", "inventario"}:
        osservati = evento.dati.get("oggetti") or [evento.dati]
        for dato in osservati:
            try:
                _catalog.enrich_observed(dato)
            except (OSError, ValueError, UnicodeError):
                # L'osservabilità non deve interrompere il runtime se una fonte web è assente.
                continue
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
