"""FastAPI/WebSocket gateway for the NosAi observability dashboard."""
from __future__ import annotations

import os
from io import BytesIO
from pathlib import Path
from typing import Any

from .ci_evidence import load_ci_evidence
from .events import DashboardEvent, DashboardEventBus
from .observability import scan_repository
from .sources import all_sources, image_reference

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.responses import FileResponse, StreamingResponse
    from fastapi.staticfiles import StaticFiles
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("Installa l'extra 'dashboard' per avviare NosAi Dashboard") from exc

app = FastAPI(title="NosAi — Centro di controllo", version="1.7")
bus = DashboardEventBus()
WEB_ROOT = Path(__file__).with_name("web")
ASSET_ROOT = WEB_ROOT / "assets"
_runtime_adapter: Any | None = None
_TEST_NAV = '<a href="/test-center" style="display:block;color:#8fe3ff;text-decoration:none;padding:11px 12px;border-radius:10px">🧪 Test & verifica</a>'

app.mount("/assets", StaticFiles(directory=ASSET_ROOT), name="dashboard-assets")


def set_runtime_adapter(adapter: Any | None) -> None:
    """Attach the observation-only runtime/client adapter."""
    global _runtime_adapter
    _runtime_adapter = adapter


def configure_nostale_observation() -> str:
    """Attach the real Windows NosTale observer when explicitly enabled."""
    global _runtime_adapter
    enabled = os.getenv("NOSAI_NOSTALE_OBSERVATION", "1").strip().lower()
    if enabled in {"0", "false", "no", "off"}:
        return "disabled"
    if os.name != "nt":
        return "non-windows"
    try:
        from app.client.nostale_windows import WindowsNosTaleAdapter
        _runtime_adapter = WindowsNosTaleAdapter()
        return "ready"
    except Exception:
        _runtime_adapter = None
        return "unavailable"


configure_nostale_observation()


def _page(name: str) -> FileResponse:
    return FileResponse(WEB_ROOT / name)


@app.get("/")
def home() -> FileResponse:
    return _page("control_center.html")


@app.get("/control-center")
def control_center() -> FileResponse:
    return _page("control_center.html")


@app.get("/runtime")
def runtime_page() -> FileResponse:
    return _page("runtime.html")


@app.get("/game-view")
def game_view() -> FileResponse:
    return _page("game_view.html")


@app.get("/diagnostics")
def diagnostics_page() -> FileResponse:
    return _page("diagnostics.html")


@app.get("/sources")
def sources_page() -> FileResponse:
    return _page("sources.html")


@app.get("/test-center")
def test_center() -> FileResponse:
    return _page("test_center.html")


@app.get("/api/test-center")
def test_center_data() -> dict[str, Any]:
    data = scan_repository()
    ci = load_ci_evidence()
    data["ci"] = ci
    junit = ci.get("junit", {}) if isinstance(ci, dict) else {}
    coverage = ci.get("coverage", {}) if isinstance(ci, dict) else {}
    security = ci.get("security", {}) if isinstance(ci, dict) else {}
    sbom = ci.get("sbom", {}) if isinstance(ci, dict) else {}
    if junit.get("status") == "FAIL":
        data["gates"]["G3"] = "FAIL"
    elif junit.get("status") == "PASS":
        data["gates"]["G3"] = "PASS"
    elif junit.get("status") == "NOT_RUN":
        data["gates"]["G3"] = "NOT_RUN"
    if coverage.get("status") == "PASS":
        data["gates"]["G6"] = "PASS"
    elif coverage.get("status") == "FAIL":
        data["gates"]["G6"] = "FAIL"
    elif coverage.get("status") == "NOT_RUN":
        data["gates"]["G6"] = "NOT_RUN"
    data["security"] = security
    data["sbom"] = sbom
    return data


@app.get("/api/stato")
def stato() -> dict[str, Any]:
    if _runtime_adapter is None:
        return {
            "connected": False,
            "stato": "pronto",
            "modalita": "sola osservazione",
            "connessione": "in attesa",
            "adapter": "nostale_windows" if os.name == "nt" else "non-windows",
        }
    from .state import snapshot_from_adapter
    return snapshot_from_adapter(_runtime_adapter).to_dict()


@app.get("/api/perception")
def perception() -> dict[str, Any]:
    """Return metadata proving whether real visual perception is available."""
    if _runtime_adapter is None:
        return {"available": False, "reason": "runtime adapter unavailable"}
    try:
        from app.client.windows_perception import WindowsNosTalePerception
        frame = WindowsNosTalePerception(_runtime_adapter).capture()
        return {
            "available": True,
            "width": frame.width,
            "height": frame.height,
            "source": frame.source,
            "observation_only": frame.observation_only,
            "screenshot_url": "/api/screenshot",
        }
    except Exception as exc:
        return {"available": False, "reason": str(exc)}


@app.get("/api/screenshot")
def screenshot() -> StreamingResponse:
    """Stream a fresh screenshot of the visible NosTale window, read-only."""
    if _runtime_adapter is None:
        return StreamingResponse(BytesIO(b""), media_type="image/png", status_code=503)
    from app.client.windows_perception import WindowsNosTalePerception
    frame = WindowsNosTalePerception(_runtime_adapter).capture()
    return StreamingResponse(BytesIO(frame.png), media_type="image/png", headers={"Cache-Control": "no-store"})


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
