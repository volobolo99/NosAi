from __future__ import annotations

from fastapi.testclient import TestClient


def test_autoset_status_endpoint() -> None:
    from app.dashboard.server import app

    client = TestClient(app)
    response = client.get('/api/autoset')
    assert response.status_code == 200
    assert response.json().get('status') in {'NOT_RUN', 'READY', 'FAIL'}


def test_autoset_endpoint_is_wired(monkeypatch) -> None:
    import app.dashboard.server as server

    expected = {
        'status': 'READY',
        'profile': {'cpu_threads': 8, 'worker_threads': 4},
        'benchmark': {'baseline': {}, 'ablations': []},
    }
    monkeypatch.setattr(server, '_last_autoset', None)
    monkeypatch.setattr('app.autoset.autoset', lambda benchmark=True: expected)
    client = TestClient(server.app)
    response = client.post('/api/autoset')
    assert response.status_code == 200
    assert response.json() == expected
