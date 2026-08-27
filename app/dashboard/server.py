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
except ImportError as exc:
    raise RuntimeError("Installa l'extra 'dashboard' per avviare NosAi Dashboard") from exc

app = FastAPI(title="NosAi — Centro di controllo", version="1.13")
bus = DashboardEventBus()
WEB_ROOT = Path(__file__).with_name("web")
ASSET_ROOT = WEB_ROOT / "assets"
_runtime_adapter: Any | None = None
_previous_frame_png: bytes | None = None
_last_autoset: dict[str, Any] | None = None
app.mount("/assets", StaticFiles(directory=ASSET_ROOT), name="dashboard-assets")


def set_runtime_adapter(adapter: Any | None) -> None:
    global _runtime_adapter, _previous_frame_png
    _runtime_adapter = adapter
    _previous_frame_png = None


def configure_nostale_observation() -> str:
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


@app.get("/ai-lab")
def ai_lab_page() -> FileResponse:
    return _page("ai_lab.html")


@app.get("/api/test-center")
def test_center_data() -> dict[str, Any]:
    data = scan_repository()
    ci = load_ci_evidence()
    data["ci"] = ci
    junit = ci.get("junit", {}) if isinstance(ci, dict) else {}
    coverage = ci.get("coverage", {}) if isinstance(ci, dict) else {}
    security = ci.get("security", {}) if isinstance(ci, dict) else {}
    sbom = ci.get("sbom", {}) if isinstance(ci, dict) else {}
    if junit.get("status") in {"FAIL", "PASS", "NOT_RUN"}:
        data["gates"]["G3"] = junit["status"]
    if coverage.get("status") in {"PASS", "FAIL", "NOT_RUN"}:
        data["gates"]["G6"] = coverage["status"]
    data["security"] = security
    data["sbom"] = sbom
    data["autoset"] = _last_autoset
    return data


@app.get("/api/ai-lab")
def ai_lab_data() -> dict[str, Any]:
    from app.ai_lab.scenarios import default_scenarios, validate_scenarios
    scenarios = default_scenarios()
    errors = validate_scenarios(scenarios)
    return {"status": "READY" if not errors else "INVALID", "mode": "offline-deterministic", "external_provider": "NOT_REQUIRED", "scenarios": len(scenarios), "candidates": 0, "results": {"PASS": 0, "FAIL": 0, "NOT_RUN": len(scenarios)}, "metrics": {"accuracy_percent": None, "safety_violation_percent": None, "p50_latency_ms": None, "p95_latency_ms": None}, "scenario_errors": errors, "evidence": None}


@app.get("/api/progression-advisor")
def progression_advisor() -> dict[str, Any]:
    """Return an advisory-only GuardAi progression report from supplied or safe demo state."""
    from time import time
    from app.progression import CharacterSnapshot, ProgressionAdvisor, ProgressionPlan, ProgressionSimulator
    snapshot = CharacterSnapshot(snapshot_id="dashboard", timestamp=time(), confidence=0.0, provenance="dashboard:no-live-snapshot")
    plans = (
        ProgressionPlan("baseline", "Percorso in-game conservativo", ("analyze", "farm", "upgrade"), 1.0, 3600.0, 0.0, 0.15),
        ProgressionPlan("efficient", "Percorso in-game orientato all'efficienza", ("analyze", "farm", "upgrade"), 1.15, 3000.0, 0.0, 0.22),
        ProgressionPlan("policy-blocked", "Scenario esterno non autorizzato", (), 2.0, 1200.0, 0.0, 0.05, policy_status="BLOCKED"),
    )
    report = ProgressionAdvisor(ProgressionSimulator(simulations=128)).evaluate(snapshot, "next progression objective", plans)
    payload = ProgressionAdvisor.dashboard_payload(report)
    payload["source_status"] = "NO_LIVE_CHARACTER_SNAPSHOT"
    payload["observation_only"] = True
    return payload


@app.post("/api/autoset")
def run_autoset() -> dict[str, Any]:
    global _last_autoset
    try:
        from app.autoset import autoset
        _last_autoset = autoset(benchmark=True)
        return _last_autoset
    except Exception as exc:
        _last_autoset = {"status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}
        return _last_autoset


@app.get("/api/autoset")
def autoset_status() -> dict[str, Any]:
    return _last_autoset or {"status": "NOT_RUN"}


@app.get("/api/stato")
def stato() -> dict[str, Any]:
    if _runtime_adapter is None:
        return {"connected": False, "stato": "pronto", "modalita": "sola osservazione", "connessione": "in attesa", "adapter": "nostale_windows" if os.name == "nt" else "non-windows"}
    from .state import snapshot_from_adapter
    return snapshot_from_adapter(_runtime_adapter).to_dict()


@app.get("/api/live-observation")
def live_observation() -> dict[str, Any]:
    if _runtime_adapter is None:
        return {"available": False, "observation_only": True, "reason": "runtime adapter unavailable"}
    try:
        from app.client.live_observation import LiveObservation
        world, _ = LiveObservation(_runtime_adapter).capture()
        world["available"] = True
        return world
    except Exception as exc:
        return {"available": False, "observation_only": True, "reason": f"{type(exc).__name__}: {exc}"}


@app.get("/api/perception")
def perception() -> dict[str, Any]:
    if _runtime_adapter is None:
        return {"available": False, "reason": "runtime adapter unavailable"}
    try:
        from app.client.windows_perception import WindowsNosTalePerception
        frame = WindowsNosTalePerception(_runtime_adapter).capture()
        return {"available": True, "width": frame.width, "height": frame.height, "source": frame.source, "observation_only": frame.observation_only, "screenshot_url": "/api/screenshot", "character_view_url": "/api/character-view"}
    except Exception as exc:
        return {"available": False, "reason": str(exc)}


@app.get("/api/screenshot")
def screenshot() -> StreamingResponse:
    if _runtime_adapter is None:
        return StreamingResponse(BytesIO(b""), media_type="image/png", status_code=503)
    from app.client.windows_perception import WindowsNosTalePerception
    frame = WindowsNosTalePerception(_runtime_adapter).capture()
    return StreamingResponse(BytesIO(frame.png), media_type="image/png", headers={"Cache-Control": "no-store"})


@app.get("/api/character-view")
def character_view() -> StreamingResponse:
    global _previous_frame_png
    if _runtime_adapter is None:
        return StreamingResponse(BytesIO(b""), media_type="image/png", status_code=503)
    try:
        from app.client.live_character_view import build_character_view
        from app.client.windows_perception import WindowsNosTalePerception
        frame = WindowsNosTalePerception(_runtime_adapter).capture()
        view = build_character_view(frame.png, _previous_frame_png)
        _previous_frame_png = frame.png
        return StreamingResponse(BytesIO(view.png), media_type="image/png", headers={"Cache-Control": "no-store", "X-NosAi-Activity": view.activity_state, "X-NosAi-Activity-Score": str(view.activity_score), "X-NosAi-Observation-Only": "true"})
    except Exception as exc:
        return StreamingResponse(BytesIO(b""), media_type="image/png", status_code=503, headers={"X-NosAi-Error": f"{type(exc).__name__}: {exc}"})


@app.get("/api/character-state")
def character_state() -> dict[str, Any]:
    if _runtime_adapter is None:
        return {"available": False, "observation_only": True, "activity": "OFFLINE", "ability": None}
    try:
        from app.client.live_character_view import build_character_view
        from app.client.windows_perception import WindowsNosTalePerception
        frame = WindowsNosTalePerception(_runtime_adapter).capture()
        view = build_character_view(frame.png, _previous_frame_png)
        return {"available": True, "observation_only": True, "activity": view.activity_state, "activity_score": view.activity_score, "ability": None, "ability_source": "not_observed"}
    except Exception as exc:
        return {"available": False, "observation_only": True, "activity": "ERROR", "ability": None, "reason": str(exc)}


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
