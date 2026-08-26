from fastapi.testclient import TestClient

from app.dashboard.server import app


client = TestClient(app)


def test_dashboard_pages_and_assets_are_reachable() -> None:
    for path in ("/", "/control-center", "/runtime", "/game-view", "/diagnostics", "/sources", "/test-center"):
        response = client.get(path)
        assert response.status_code == 200
        assert "NosAi" in response.text

    asset = client.get("/assets/css/nosai.css")
    assert asset.status_code == 200
    assert "--cyan" in asset.text


def test_runtime_and_sources_api_are_safe_without_client() -> None:
    runtime = client.get("/api/stato")
    assert runtime.status_code == 200
    assert runtime.json()["connected"] is False

    sources = client.get("/api/fonti")
    assert sources.status_code == 200
    assert isinstance(sources.json(), dict)


def test_websocket_connects() -> None:
    with client.websocket_connect("/ws") as websocket:
        message = websocket.receive_json()
        assert message["tipo"] == "connessione"
        assert message["stato"] == "connesso"
