"""FastAPI/WebSocket gateway for the NosAi observability dashboard."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .catalog import ItemCatalog
from .events import DashboardEvent, DashboardEventBus
from .runtime_bridge import RuntimeDashboardStreamer
from .sources import all_sources, image_reference
from .state import snapshot_from_adapter

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.responses import FileResponse
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("Installa l'extra 'dashboard' per avviare NosAi Dashboard") from exc

app = FastAPI(title="NosAi — Centro di controllo", version="1.4")
bus = DashboardEventBus()
WEB_ROOT = Path(__file__).with_name("web")
_runtime_adapter: Any | None = None
_streamer: RuntimeDashboardStreamer | None = None
_catalog = ItemCatalog()


def set_runtime_adapter(adapter: Any | None) -> None:
    global _runtime_adapter
    _runtime_adapter = adapter


@app.on_event("startup")
async def _start_runtime_stream() -> None:
    global _streamer
    if _runtime_adapter is not None:
        _streamer = RuntimeDashboardStreamer(_runtime_adapter, bus, interval_s=0.5)
        _streamer.start()


@app.on_event("shutdown")
async def _stop_runtime_stream() -> None:
    global _streamer
    if _streamer is not None:
        await _streamer.stop()
        _streamer = None
    if _runtime_adapter is not None:
        close = getattr(_runtime_adapter, "close", None)
        if callable(close):
            close()


@app.get("/")
def home() -> FileResponse:
    return FileResponse(WEB_ROOT / "index.html")


@app.get("/api/stato")
def stato() -> dict[str, Any]:
    if _runtime_adapter is None:
        return {"stato": "pronto", "modalita": "sola osservazione", "connessione": "in attesa"}
    return snapshot_from_adapter(_runtime_adapter).to_dict()


@app.get("/api/sonda-client")
def sonda_client() -> dict[str, Any]:
    if _runtime_adapter is None:
        return {"connesso": False, "stato_valido": False, "azione_valida": False, "dettaglio": "nessun adapter collegato"}
    from app.client.adapter_runtime import probe_client
    result = probe_client(_runtime_adapter)
    return {"connesso": result.connected, "stato_valido": result.state_valid, "azione_valida": result.action_valid, "dettaglio": result.detail}


@app.get("/api/percezione")
def percezione() -> dict[str, Any]:
    """Capture one real frame and optionally enrich it with OpenAI vision."""
    if _runtime_adapter is None:
        return {"disponibile": False, "dettaglio": "nessun adapter collegato"}
    capture = getattr(_runtime_adapter, "capture_screen", None)
    if not callable(capture):
        return {"disponibile": False, "dettaglio": "adapter senza cattura schermo"}
    try:
        frame = capture()
        from app.client.vision_observation import analyze_frame
        observation = analyze_frame(frame)
        return {"disponibile": True, "larghezza": frame.width, "altezza": frame.height, "osservazione": observation.to_dict()}
    except Exception as exc:  # safe boundary: perception cannot stop runtime
        return {"disponibile": False, "dettaglio": str(exc)}


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
    if evento.tipo in {"item_rilevato", "inventario"}:
        osservati = evento.dati.get("oggetti") or [evento.dati]
        for dato in osservati:
            try:
                _catalog.enrich_observed(dato)
            except (OSError, ValueError, UnicodeError):
                continue
    bus.publish(evento)
    return {"stato": "pubblicato"}


@app.websocket("/ws")
async def websocket(websocket: WebSocket) -> None:
    await websocket.accept()
    queue = bus.subscribe()
    try:
        await websocket.send_json({"tipo": "connessione", "stato": "connesso", "modalita": "sola osservazione"})
        while True:
            event = await queue.get()
            await websocket.send_json(event.to_dict())
    except WebSocketDisconnect:
        pass
    finally:
        bus.unsubscribe(queue)
