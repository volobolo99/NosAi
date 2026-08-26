"""FastAPI/WebSocket gateway for the NosAi observability dashboard."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .events import DashboardEvent, DashboardEventBus
from .observability import scan_repository
from .sources import all_sources, image_reference

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse, FileResponse
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("Installa l'extra 'dashboard' per avviare NosAi Dashboard") from exc

app = FastAPI(title="NosAi — Centro di controllo", version="1.2")
bus = DashboardEventBus()
WEB_ROOT = Path(__file__).with_name("web")
_runtime_adapter: Any | None = None
_TEST_NAV = '<a href="/test-center" style="display:block;color:#8fe3ff;text-decoration:none;padding:11px 12px;border-radius:10px">🧪 Test & verifica</a>'


def set_runtime_adapter(adapter: Any | None) -> None:
    """Attach the observation-only runtime/client adapter."""
    global _runtime_adapter
    _runtime_adapter = adapter


@app.get("/")
def home() -> HTMLResponse:
    html = (WEB_ROOT / "index.html").read_text(encoding="utf-8")
    html = html.replace("</nav>", f"{_TEST_NAV}</nav>", 1)
    return HTMLResponse(html)


@app.get("/test-center")
def test_center() -> FileResponse:
    return FileResponse(WEB_ROOT / "test_center.html")


@app.get("/api/test-center")
def test_center_data() -> dict[str, Any]:
    return scan_repository()


@app.get("/api/stato")
def stato() -> dict[str, Any]:
    if _runtime_adapter is None:
        return {"stato": "pronto", "modalita": "sola osservazione", "connessione": "in attesa"}
    from .state import snapshot_from_adapter
    return snapshot_from_adapter(_runtime_adapter).to_dict()


@app.get("/api/fonti")
def fonti() -> dict[str, str]:
    return all_sources()


@app.get("/api/immagine-oggetto")
def immagine_oggetto(image_url: str | None = None) -> dict[str, str | None]:
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
