from pathlib import Path

import pytest

from app.evolution_lab.online_provider import OnlineResearchConfig, OnlineResearchError, search_json


def test_online_provider_normalizes_findings(monkeypatch: pytest.MonkeyPatch) -> None:
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return b'{"findings":[{"finding_id":"f1","source":"provider","title":"x","summary":"y","relevance":1,"reliability":1,"freshness":1}]}'
    monkeypatch.setattr("app.evolution_lab.online_provider.urlopen", lambda *a, **k: Response())
    result = search_json(OnlineResearchConfig("https://example.invalid/search"), "test")
    assert result.findings[0].finding_id == "f1"
    assert result.findings[0].source == "provider"


def test_online_provider_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*args, **kwargs): raise OSError("offline")
    monkeypatch.setattr("app.evolution_lab.online_provider.urlopen", fail)
    with pytest.raises(OnlineResearchError):
        search_json(OnlineResearchConfig("https://example.invalid/search"), "test")
